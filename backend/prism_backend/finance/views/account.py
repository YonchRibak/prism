from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import Account
from ..serializers import AccountSerializer, AccountSummarySerializer
from decimal import Decimal


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    All accounts are scoped to the authenticated user.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['account_type', 'is_active']
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['name']
    search_fields = ['name']

    def get_queryset(self):
        """Return accounts for the authenticated user only"""
        return Account.objects.filter(owner=self.request.user)

    def destroy(self, request, pk=None):
        """Delete an account with transaction check"""
        try:
            account = self.get_object()

            # Check if account has transactions
            if account.transactions.exists():
                return Response(
                    {'error': 'Cannot delete account with existing transactions'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            account.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get account summary statistics"""
        accounts = self.get_queryset()

        total_balance = sum(account.balance for account in accounts)
        account_counts = {}

        for account in accounts:
            account_type = account.account_type
            if account_type not in account_counts:
                account_counts[account_type] = {'count': 0, 'balance': Decimal('0.00')}
            account_counts[account_type]['count'] += 1
            account_counts[account_type]['balance'] += account.balance

        summary_data = {
            'total_accounts': accounts.count(),
            'total_balance': total_balance,
            'active_accounts': accounts.filter(is_active=True).count(),
            'by_type': {k: {'count': v['count'], 'balance': v['balance']}
                       for k, v in account_counts.items()}
        }

        serializer = AccountSummarySerializer(summary_data)
        return Response(serializer.data)