from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import datetime
from decimal import Decimal
from ..models import Budget
from ..serializers import BudgetSerializer, BudgetCreateSerializer, BudgetSummarySerializer


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
        queryset = Budget.objects.filter(owner=self.request.user)

        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(end_date__lte=end_date)
            except ValueError:
                pass

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BudgetCreateSerializer
        return BudgetSerializer

    def create(self, request, *args, **kwargs):
        """Create budget with proper serializer"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            budget = serializer.save()
            # Return with the full serializer for response
            response_serializer = BudgetSerializer(budget, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active budgets"""
        today = datetime.now().date()
        queryset = self.get_queryset().filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def over_budget(self, request):
        """Get budgets that are over their limit"""
        budgets = []
        for budget in self.get_queryset().filter(is_active=True):
            if budget.is_over_budget:
                budgets.append(budget)

        serializer = self.get_serializer(budgets, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get budget summary statistics"""
        queryset = self.get_queryset().filter(is_active=True)

        total_budgets = queryset.count()
        total_budget_amount = sum(budget.amount for budget in queryset)
        total_spent = sum(budget.spent_amount for budget in queryset)
        over_budget_count = sum(1 for budget in queryset if budget.is_over_budget)

        summary_data = {
            'total_budgets': total_budgets,
            'total_budget_amount': total_budget_amount,
            'total_spent': total_spent,
            'total_remaining': total_budget_amount - total_spent,
            'over_budget_count': over_budget_count,
            'on_track_count': total_budgets - over_budget_count,
        }

        serializer = BudgetSummarySerializer(summary_data)
        return Response(serializer.data)