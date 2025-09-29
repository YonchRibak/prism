from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import Budget, Category


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing budgets.
    All budgets are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category', 'period', 'is_active']
    ordering_fields = ['name', 'amount', 'start_date', 'created_at']
    ordering = ['-start_date']
    search_fields = ['name']

    def get_queryset(self):
        """Return budgets for the authenticated user only"""
        return Budget.objects.filter(owner=self.request.user)

    def get_serializer_data(self, instance):
        """Convert budget instance to serializer data"""
        return {
            'id': instance.id,
            'name': instance.name,
            'category': {
                'id': instance.category.id,
                'name': instance.category.name,
                'full_name': instance.category.full_name
            },
            'amount': str(instance.amount),
            'period': instance.period,
            'period_display': instance.get_period_display(),
            'start_date': instance.start_date,
            'end_date': instance.end_date,
            'spent_amount': str(instance.spent_amount),
            'remaining_amount': str(instance.remaining_amount),
            'percentage_used': round(instance.percentage_used, 2),
            'is_over_budget': instance.is_over_budget,
            'is_active': instance.is_active,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

    def list(self, request):
        """List budgets with optional date filtering"""
        queryset = self.filter_queryset(self.get_queryset())

        # Date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__gte=start_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(end_date__lte=end_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        budgets = [self.get_serializer_data(budget) for budget in queryset]

        return Response({
            'count': len(budgets),
            'results': budgets
        })

    def retrieve(self, request, pk=None):
        """Get a specific budget"""
        try:
            budget = self.get_queryset().get(pk=pk)
            return Response(self.get_serializer_data(budget))
        except Budget.DoesNotExist:
            return Response(
                {'error': 'Budget not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """Create a new budget"""
        try:
            data = request.data

            # Validate required fields
            required_fields = ['name', 'category_id', 'amount', 'start_date', 'end_date']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Get category
            try:
                category = Category.objects.get(pk=data['category_id'], owner=request.user)
            except Category.DoesNotExist:
                return Response(
                    {'error': 'Category not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Parse dates
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate date range
            if end_date <= start_date:
                return Response(
                    {'error': 'End date must be after start date'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check for overlapping budgets for the same category
            overlapping = Budget.objects.filter(
                owner=request.user,
                category=category,
                is_active=True
            ).filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )

            if overlapping.exists():
                return Response(
                    {'error': 'Budget period overlaps with existing budget for this category'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create budget
            budget = Budget.objects.create(
                owner=request.user,
                category=category,
                name=data['name'],
                amount=Decimal(str(data['amount'])),
                period=data.get('period', 'monthly'),
                start_date=start_date,
                end_date=end_date,
                is_active=data.get('is_active', True)
            )

            return Response(
                self.get_serializer_data(budget),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Update a budget"""
        try:
            budget = self.get_queryset().get(pk=pk)
            data = request.data

            # Update category if provided
            if 'category_id' in data:
                try:
                    category = Category.objects.get(pk=data['category_id'], owner=request.user)
                    budget.category = category
                except Category.DoesNotExist:
                    return Response(
                        {'error': 'Category not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Update dates if provided
            start_date = budget.start_date
            end_date = budget.end_date

            if 'start_date' in data:
                try:
                    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if 'end_date' in data:
                try:
                    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Validate date range
            if end_date <= start_date:
                return Response(
                    {'error': 'End date must be after start date'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            budget.start_date = start_date
            budget.end_date = end_date

            # Update other fields
            updatable_fields = ['name', 'amount', 'period', 'is_active']

            for field in updatable_fields:
                if field in data:
                    if field == 'amount':
                        setattr(budget, field, Decimal(str(data[field])))
                    else:
                        setattr(budget, field, data[field])

            budget.save()

            return Response(self.get_serializer_data(budget))

        except Budget.DoesNotExist:
            return Response(
                {'error': 'Budget not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Delete a budget"""
        try:
            budget = self.get_queryset().get(pk=pk)
            budget.delete()

            return Response(
                {'message': 'Budget deleted successfully'},
                status=status.HTTP_200_OK
            )

        except Budget.DoesNotExist:
            return Response(
                {'error': 'Budget not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active budgets"""
        today = datetime.now().date()
        queryset = self.get_queryset().filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )

        budgets = [self.get_serializer_data(budget) for budget in queryset]

        return Response({
            'count': len(budgets),
            'results': budgets
        })

    @action(detail=False, methods=['get'])
    def over_budget(self, request):
        """Get budgets that are over their limit"""
        budgets = []
        for budget in self.get_queryset().filter(is_active=True):
            if budget.is_over_budget:
                budgets.append(self.get_serializer_data(budget))

        return Response({
            'count': len(budgets),
            'results': budgets
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get budget summary statistics"""
        queryset = self.get_queryset().filter(is_active=True)

        total_budgets = queryset.count()
        total_budget_amount = sum(budget.amount for budget in queryset)
        total_spent = sum(budget.spent_amount for budget in queryset)
        over_budget_count = sum(1 for budget in queryset if budget.is_over_budget)

        return Response({
            'total_budgets': total_budgets,
            'total_budget_amount': str(total_budget_amount),
            'total_spent': str(total_spent),
            'total_remaining': str(total_budget_amount - total_spent),
            'over_budget_count': over_budget_count,
            'on_track_count': total_budgets - over_budget_count,
        })