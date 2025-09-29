from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import Transaction, Account, Category


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
        return Transaction.objects.filter(owner=self.request.user)

    def get_serializer_data(self, instance):
        """Convert transaction instance to serializer data"""
        return {
            'id': instance.id,
            'account': {
                'id': instance.account.id,
                'name': instance.account.name,
                'account_type': instance.account.account_type
            },
            'category': {
                'id': instance.category.id,
                'name': instance.category.name,
                'full_name': instance.category.full_name
            } if instance.category else None,
            'amount': str(instance.amount),
            'description': instance.description,
            'date': instance.date,
            'notes': instance.notes,
            'transfer_to': {
                'id': instance.transfer_to.id,
                'name': instance.transfer_to.name
            } if instance.transfer_to else None,
            'is_recurring': instance.is_recurring,
            'recurring_frequency': instance.recurring_frequency,
            'is_expense': instance.is_expense,
            'is_income': instance.is_income,
            'is_transfer': instance.is_transfer,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

    def list(self, request):
        """List transactions with optional date filtering"""
        queryset = self.filter_queryset(self.get_queryset())

        # Date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        offset = (page - 1) * page_size

        total_count = queryset.count()
        transactions = queryset[offset:offset + page_size]

        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'results': [self.get_serializer_data(transaction) for transaction in transactions]
        })

    def retrieve(self, request, pk=None):
        """Get a specific transaction"""
        try:
            transaction = self.get_queryset().get(pk=pk)
            return Response(self.get_serializer_data(transaction))
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """Create a new transaction"""
        try:
            data = request.data

            # Validate required fields
            required_fields = ['account_id', 'amount', 'description', 'date']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Get account
            try:
                account = Account.objects.get(pk=data['account_id'], owner=request.user)
            except Account.DoesNotExist:
                return Response(
                    {'error': 'Account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get category (optional)
            category = None
            if data.get('category_id'):
                try:
                    category = Category.objects.get(pk=data['category_id'], owner=request.user)
                except Category.DoesNotExist:
                    return Response(
                        {'error': 'Category not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Get transfer account (optional)
            transfer_to = None
            if data.get('transfer_to_id'):
                try:
                    transfer_to = Account.objects.get(pk=data['transfer_to_id'], owner=request.user)
                except Account.DoesNotExist:
                    return Response(
                        {'error': 'Transfer account not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Parse date
            try:
                transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create transaction
            transaction = Transaction.objects.create(
                owner=request.user,
                account=account,
                category=category,
                amount=Decimal(str(data['amount'])),
                description=data['description'],
                date=transaction_date,
                notes=data.get('notes', ''),
                transfer_to=transfer_to,
                is_recurring=data.get('is_recurring', False),
                recurring_frequency=data.get('recurring_frequency')
            )

            return Response(
                self.get_serializer_data(transaction),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Update a transaction"""
        try:
            transaction = self.get_queryset().get(pk=pk)
            data = request.data

            # Update account if provided
            if 'account_id' in data:
                try:
                    account = Account.objects.get(pk=data['account_id'], owner=request.user)
                    transaction.account = account
                except Account.DoesNotExist:
                    return Response(
                        {'error': 'Account not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Update category if provided
            if 'category_id' in data:
                if data['category_id']:
                    try:
                        category = Category.objects.get(pk=data['category_id'], owner=request.user)
                        transaction.category = category
                    except Category.DoesNotExist:
                        return Response(
                            {'error': 'Category not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                else:
                    transaction.category = None

            # Update other fields
            updatable_fields = ['amount', 'description', 'date', 'notes', 'is_recurring', 'recurring_frequency']

            for field in updatable_fields:
                if field in data:
                    if field == 'date':
                        try:
                            transaction.date = datetime.strptime(data[field], '%Y-%m-%d').date()
                        except ValueError:
                            return Response(
                                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    elif field == 'amount':
                        transaction.amount = Decimal(str(data[field]))
                    else:
                        setattr(transaction, field, data[field])

            transaction.save()

            return Response(self.get_serializer_data(transaction))

        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Delete a transaction"""
        try:
            transaction = self.get_queryset().get(pk=pk)
            transaction.delete()

            return Response(
                {'message': 'Transaction deleted successfully'},
                status=status.HTTP_200_OK
            )

        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary statistics"""
        queryset = self.get_queryset()

        # Date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

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

        # Calculate totals
        total_income = queryset.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_expenses = abs(queryset.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'))
        net_income = total_income - total_expenses

        return Response({
            'total_transactions': queryset.count(),
            'total_income': str(total_income),
            'total_expenses': str(total_expenses),
            'net_income': str(net_income),
            'income_transactions': queryset.filter(amount__gt=0).count(),
            'expense_transactions': queryset.filter(amount__lt=0).count(),
            'transfer_transactions': queryset.filter(transfer_to__isnull=False).count(),
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent transactions (last 30 days)"""
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        queryset = self.get_queryset().filter(date__gte=thirty_days_ago)

        limit = int(request.query_params.get('limit', 10))
        transactions = queryset[:limit]

        return Response({
            'count': len(transactions),
            'results': [self.get_serializer_data(transaction) for transaction in transactions]
        })