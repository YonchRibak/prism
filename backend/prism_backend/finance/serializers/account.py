from rest_framework import serializers
from ..models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Account model with user ownership validation.
    """
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Account
        fields = [
            'id', 'name', 'account_type', 'account_type_display',
            'balance', 'is_active', 'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Validate account name is unique for the user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            # Check if account with this name already exists for this user
            existing = Account.objects.filter(owner=user, name=value)

            # Exclude current instance if updating
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    "You already have an account with this name."
                )
        return value

    def validate_balance(self, value):
        """Validate balance is reasonable."""
        if value < -999999999:
            raise serializers.ValidationError("Balance cannot be less than -999,999,999")
        if value > 999999999:
            raise serializers.ValidationError("Balance cannot be more than 999,999,999")
        return value

    def create(self, validated_data):
        """Create account with owner set to current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class AccountCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for account creation.
    """
    class Meta:
        model = Account
        fields = [
            'name', 'account_type', 'balance', 'is_active'
        ]

    def validate_name(self, value):
        """Validate account name is unique for the user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if Account.objects.filter(owner=user, name=value).exists():
                raise serializers.ValidationError(
                    "You already have an account with this name."
                )
        return value

    def validate_balance(self, value):
        """Validate balance is reasonable."""
        if value < -999999999:
            raise serializers.ValidationError("Balance cannot be less than -999,999,999")
        if value > 999999999:
            raise serializers.ValidationError("Balance cannot be more than 999,999,999")
        return value

    def create(self, validated_data):
        """Create account with owner set to current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class AccountSummarySerializer(serializers.Serializer):
    """
    Serializer for account summary statistics.
    """
    total_accounts = serializers.IntegerField()
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_accounts = serializers.IntegerField()
    by_type = serializers.DictField()