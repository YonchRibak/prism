from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import Transaction
from ..serializers import TransactionSerializer, TransactionCreateSerializer, TransactionSummarySerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial transactions.
    All transactions are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['account', 'category', 'is_recurring']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    search_fields = ['description', 'notes']

    def get_queryset(self):
        """Return transactions for the authenticated user only"""
        queryset = Transaction.objects.filter(owner=self.request.user)

        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer

    def create(self, request, *args, **kwargs):
        """Create transaction with proper serializer"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save()
            # Return with the full serializer for response
            response_serializer = TransactionSerializer(transaction, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary statistics"""
        queryset = self.get_queryset()

        # Calculate totals
        income_total = queryset.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        expense_total = abs(queryset.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'))
        net_income = income_total - expense_total

        summary_data = {
            'total_transactions': queryset.count(),
            'total_income': income_total,
            'total_expenses': expense_total,
            'net_income': net_income,
            'income_transactions': queryset.filter(amount__gt=0).count(),
            'expense_transactions': queryset.filter(amount__lt=0).count(),
            'transfer_transactions': queryset.filter(transfer_to__isnull=False).count(),
        }

        serializer = TransactionSummarySerializer(summary_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent transactions (last 30 days)"""
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        queryset = self.get_queryset().filter(date__gte=thirty_days_ago)

        limit = int(request.query_params.get('limit', 10))
        transactions = queryset[:limit]

        serializer = self.get_serializer(transactions, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })