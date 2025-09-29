from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import datetime
from decimal import Decimal
from ..models import Goal, Account


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial goals.
    All goals are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['goal_type', 'is_active', 'is_completed', 'linked_account']
    ordering_fields = ['name', 'target_amount', 'target_date', 'created_at']
    ordering = ['-created_at']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Return goals for the authenticated user only"""
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_data(self, instance):
        """Convert goal instance to serializer data"""
        return {
            'id': instance.id,
            'name': instance.name,
            'description': instance.description,
            'goal_type': instance.goal_type,
            'goal_type_display': instance.get_goal_type_display(),
            'target_amount': str(instance.target_amount),
            'current_amount': str(instance.current_amount),
            'remaining_amount': str(instance.remaining_amount),
            'progress_percentage': round(instance.progress_percentage, 2),
            'target_date': instance.target_date,
            'linked_account': {
                'id': instance.linked_account.id,
                'name': instance.linked_account.name
            } if instance.linked_account else None,
            'is_active': instance.is_active,
            'is_completed': instance.is_completed,
            'is_goal_reached': instance.is_goal_reached,
            'completed_at': instance.completed_at,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

    def list(self, request):
        """List goals"""
        queryset = self.filter_queryset(self.get_queryset())
        goals = [self.get_serializer_data(goal) for goal in queryset]

        return Response({
            'count': len(goals),
            'results': goals
        })

    def retrieve(self, request, pk=None):
        """Get a specific goal"""
        try:
            goal = self.get_queryset().get(pk=pk)
            return Response(self.get_serializer_data(goal))
        except Goal.DoesNotExist:
            return Response(
                {'error': 'Goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """Create a new goal"""
        try:
            data = request.data

            # Validate required fields
            required_fields = ['name', 'target_amount']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Get linked account (optional)
            linked_account = None
            if data.get('linked_account_id'):
                try:
                    linked_account = Account.objects.get(
                        pk=data['linked_account_id'],
                        owner=request.user
                    )
                except Account.DoesNotExist:
                    return Response(
                        {'error': 'Linked account not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Parse target date (optional)
            target_date = None
            if data.get('target_date'):
                try:
                    target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Invalid target_date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create goal
            goal = Goal.objects.create(
                owner=request.user,
                name=data['name'],
                description=data.get('description', ''),
                goal_type=data.get('goal_type', 'savings'),
                target_amount=Decimal(str(data['target_amount'])),
                current_amount=Decimal(str(data.get('current_amount', '0.00'))),
                target_date=target_date,
                linked_account=linked_account,
                is_active=data.get('is_active', True)
            )

            return Response(
                self.get_serializer_data(goal),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Update a goal"""
        try:
            goal = self.get_queryset().get(pk=pk)
            data = request.data

            # Update linked account if provided
            if 'linked_account_id' in data:
                if data['linked_account_id']:
                    try:
                        linked_account = Account.objects.get(
                            pk=data['linked_account_id'],
                            owner=request.user
                        )
                        goal.linked_account = linked_account
                    except Account.DoesNotExist:
                        return Response(
                            {'error': 'Linked account not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                else:
                    goal.linked_account = None

            # Update target date if provided
            if 'target_date' in data:
                if data['target_date']:
                    try:
                        goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
                    except ValueError:
                        return Response(
                            {'error': 'Invalid target_date format. Use YYYY-MM-DD'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    goal.target_date = None

            # Update other fields
            updatable_fields = ['name', 'description', 'goal_type', 'target_amount', 'current_amount', 'is_active']

            for field in updatable_fields:
                if field in data:
                    if field in ['target_amount', 'current_amount']:
                        setattr(goal, field, Decimal(str(data[field])))
                    else:
                        setattr(goal, field, data[field])

            goal.save()

            return Response(self.get_serializer_data(goal))

        except Goal.DoesNotExist:
            return Response(
                {'error': 'Goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Delete a goal"""
        try:
            goal = self.get_queryset().get(pk=pk)
            goal.delete()

            return Response(
                {'message': 'Goal deleted successfully'},
                status=status.HTTP_200_OK
            )

        except Goal.DoesNotExist:
            return Response(
                {'error': 'Goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update goal progress by adding/subtracting amount"""
        try:
            goal = self.get_queryset().get(pk=pk)
            data = request.data

            if 'amount' not in data:
                return Response(
                    {'error': 'amount is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            amount_change = Decimal(str(data['amount']))
            new_amount = goal.current_amount + amount_change

            # Ensure current amount doesn't go below 0
            if new_amount < 0:
                return Response(
                    {'error': 'Current amount cannot be negative'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            goal.update_progress(new_amount)

            return Response(self.get_serializer_data(goal))

        except Goal.DoesNotExist:
            return Response(
                {'error': 'Goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active goals"""
        queryset = self.get_queryset().filter(is_active=True, is_completed=False)
        goals = [self.get_serializer_data(goal) for goal in queryset]

        return Response({
            'count': len(goals),
            'results': goals
        })

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed goals"""
        queryset = self.get_queryset().filter(is_completed=True)
        goals = [self.get_serializer_data(goal) for goal in queryset]

        return Response({
            'count': len(goals),
            'results': goals
        })

    @action(detail=False, methods=['get'])
    def near_target(self, request):
        """Get goals that are close to their target (>80% progress)"""
        goals = []
        for goal in self.get_queryset().filter(is_active=True, is_completed=False):
            if goal.progress_percentage >= 80:
                goals.append(self.get_serializer_data(goal))

        return Response({
            'count': len(goals),
            'results': goals
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get goal summary statistics"""
        queryset = self.get_queryset()

        total_goals = queryset.count()
        active_goals = queryset.filter(is_active=True, is_completed=False).count()
        completed_goals = queryset.filter(is_completed=True).count()

        total_target_amount = sum(goal.target_amount for goal in queryset.filter(is_active=True))
        total_saved_amount = sum(goal.current_amount for goal in queryset.filter(is_active=True))

        # Goals by type
        goal_types = {}
        for goal in queryset:
            goal_type = goal.goal_type
            if goal_type not in goal_types:
                goal_types[goal_type] = {'count': 0, 'target_amount': Decimal('0.00'), 'saved_amount': Decimal('0.00')}
            goal_types[goal_type]['count'] += 1
            goal_types[goal_type]['target_amount'] += goal.target_amount
            goal_types[goal_type]['saved_amount'] += goal.current_amount

        return Response({
            'total_goals': total_goals,
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'total_target_amount': str(total_target_amount),
            'total_saved_amount': str(total_saved_amount),
            'total_remaining_amount': str(total_target_amount - total_saved_amount),
            'average_progress': round(
                (total_saved_amount / total_target_amount * 100) if total_target_amount > 0 else 0,
                2
            ),
            'by_type': {k: {
                'count': v['count'],
                'target_amount': str(v['target_amount']),
                'saved_amount': str(v['saved_amount'])
            } for k, v in goal_types.items()}
        })