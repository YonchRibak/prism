from rest_framework import serializers
from decimal import Decimal
from ..models import Transaction, Account, Category


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model with related data.
    """
    owner = serializers.StringRelatedField(read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_full_name = serializers.CharField(source='category.full_name', read_only=True)
    transfer_to_name = serializers.CharField(source='transfer_to.name', read_only=True)
    is_expense = serializers.BooleanField(read_only=True)
    is_income = serializers.BooleanField(read_only=True)
    is_transfer = serializers.BooleanField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'account', 'account_name', 'category', 'category_name',
            'category_full_name', 'amount', 'description', 'date', 'notes',
            'transfer_to', 'transfer_to_name', 'is_recurring', 'recurring_frequency',
            'is_expense', 'is_income', 'is_transfer', 'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_account(self, value):
        """Validate account belongs to the current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.owner != request.user:
                raise serializers.ValidationError("Account must belong to you.")
        return value

    def validate_category(self, value):
        """Validate category belongs to the current user if provided."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                if value.owner != request.user:
                    raise serializers.ValidationError("Category must belong to you.")
        return value

    def validate_transfer_to(self, value):
        """Validate transfer account belongs to the current user if provided."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                if value.owner != request.user:
                    raise serializers.ValidationError("Transfer account must belong to you.")

                # Prevent transfers to the same account
                account = self.initial_data.get('account')
                if account and value.id == account:
                    raise serializers.ValidationError("Cannot transfer to the same account.")
        return value

    def validate_amount(self, value):
        """Validate transaction amount."""
        if value == 0:
            raise serializers.ValidationError("Amount cannot be zero.")
        if abs(value) > Decimal('999999999.99'):
            raise serializers.ValidationError("Amount cannot exceed 999,999,999.99.")
        return value

    def validate_recurring_frequency(self, value):
        """Validate recurring frequency is provided if is_recurring is True."""
        is_recurring = self.initial_data.get('is_recurring', False)
        if is_recurring and not value:
            raise serializers.ValidationError(
                "Recurring frequency is required when is_recurring is True."
            )
        return value

    def validate(self, attrs):
        """Validate transaction data consistency."""
        # If transfer_to is set, ensure category is not set
        if attrs.get('transfer_to') and attrs.get('category'):
            raise serializers.ValidationError(
                "Transfer transactions should not have a category."
            )

        return attrs

    def create(self, validated_data):
        """Create transaction with owner set to current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for transaction creation with ID-based relationships.
    """
    account_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    transfer_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            'account_id', 'category_id', 'amount', 'description', 'date',
            'notes', 'transfer_to_id', 'is_recurring', 'recurring_frequency'
        ]

    def validate_account_id(self, value):
        """Validate account exists and belongs to user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                account = Account.objects.get(id=value, owner=request.user)
                return value
            except Account.DoesNotExist:
                raise serializers.ValidationError("Account not found or does not belong to you.")
        return value

    def validate_category_id(self, value):
        """Validate category exists and belongs to user if provided."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    category = Category.objects.get(id=value, owner=request.user)
                    return value
                except Category.DoesNotExist:
                    raise serializers.ValidationError("Category not found or does not belong to you.")
        return value

    def validate_transfer_to_id(self, value):
        """Validate transfer account exists and belongs to user if provided."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    account = Account.objects.get(id=value, owner=request.user)
                    return value
                except Account.DoesNotExist:
                    raise serializers.ValidationError("Transfer account not found or does not belong to you.")
        return value

    def validate(self, attrs):
        """Validate transaction consistency."""
        # Prevent transfers to the same account
        if attrs.get('transfer_to_id') and attrs.get('account_id'):
            if attrs['transfer_to_id'] == attrs['account_id']:
                raise serializers.ValidationError("Cannot transfer to the same account.")

        # If transfer_to_id is set, category_id should not be set
        if attrs.get('transfer_to_id') and attrs.get('category_id'):
            raise serializers.ValidationError(
                "Transfer transactions should not have a category."
            )

        return attrs

    def create(self, validated_data):
        """Create transaction with proper model relationships."""
        request = self.context.get('request')
        user = request.user

        # Convert IDs to model instances
        account_id = validated_data.pop('account_id')
        account = Account.objects.get(id=account_id, owner=user)

        category_id = validated_data.pop('category_id', None)
        category = None
        if category_id:
            category = Category.objects.get(id=category_id, owner=user)

        transfer_to_id = validated_data.pop('transfer_to_id', None)
        transfer_to = None
        if transfer_to_id:
            transfer_to = Account.objects.get(id=transfer_to_id, owner=user)

        # Create transaction
        transaction = Transaction.objects.create(
            owner=user,
            account=account,
            category=category,
            transfer_to=transfer_to,
            **validated_data
        )

        return transaction


class TransactionSummarySerializer(serializers.Serializer):
    """
    Serializer for transaction summary statistics.
    """
    total_transactions = serializers.IntegerField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    income_transactions = serializers.IntegerField()
    expense_transactions = serializers.IntegerField()
    transfer_transactions = serializers.IntegerField()