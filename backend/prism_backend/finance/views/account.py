from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import Account
from decimal import Decimal


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    All accounts are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['account_type', 'is_active']
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['name']
    search_fields = ['name']

    def get_queryset(self):
        """Return accounts for the authenticated user only"""
        return Account.objects.filter(owner=self.request.user)

    def get_serializer_data(self, instance):
        """Convert account instance to serializer data"""
        return {
            'id': instance.id,
            'name': instance.name,
            'account_type': instance.account_type,
            'account_type_display': instance.get_account_type_display(),
            'balance': str(instance.balance),
            'is_active': instance.is_active,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

    def list(self, request):
        """List all user accounts"""
        queryset = self.filter_queryset(self.get_queryset())
        accounts = [self.get_serializer_data(account) for account in queryset]

        return Response({
            'count': len(accounts),
            'results': accounts
        })

    def retrieve(self, request, pk=None):
        """Get a specific account"""
        try:
            account = self.get_queryset().get(pk=pk)
            return Response(self.get_serializer_data(account))
        except Account.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """Create a new account"""
        try:
            data = request.data

            # Validate required fields
            required_fields = ['name', 'account_type']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Check for duplicate name
            if Account.objects.filter(owner=request.user, name=data['name']).exists():
                return Response(
                    {'error': 'Account with this name already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create account
            account = Account.objects.create(
                owner=request.user,
                name=data['name'],
                account_type=data['account_type'],
                balance=Decimal(str(data.get('balance', '0.00'))),
                is_active=data.get('is_active', True)
            )

            return Response(
                self.get_serializer_data(account),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Update an account"""
        try:
            account = self.get_queryset().get(pk=pk)
            data = request.data

            # Update fields
            updatable_fields = ['name', 'account_type', 'balance', 'is_active']

            for field in updatable_fields:
                if field in data:
                    if field == 'name':
                        # Check for duplicate name
                        if (data[field] != account.name and
                            Account.objects.filter(owner=request.user, name=data[field]).exists()):
                            return Response(
                                {'error': 'Account with this name already exists'},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                    if field == 'balance':
                        setattr(account, field, Decimal(str(data[field])))
                    else:
                        setattr(account, field, data[field])

            account.save()

            return Response(self.get_serializer_data(account))

        except Account.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Delete an account"""
        try:
            account = self.get_queryset().get(pk=pk)

            # Check if account has transactions
            if account.transactions.exists():
                return Response(
                    {'error': 'Cannot delete account with existing transactions'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            account.delete()

            return Response(
                {'message': 'Account deleted successfully'},
                status=status.HTTP_200_OK
            )

        except Account.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )
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

        return Response({
            'total_accounts': accounts.count(),
            'total_balance': str(total_balance),
            'active_accounts': accounts.filter(is_active=True).count(),
            'by_type': {k: {'count': v['count'], 'balance': str(v['balance'])}
                       for k, v in account_counts.items()}
        })