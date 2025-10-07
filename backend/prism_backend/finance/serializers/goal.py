from rest_framework import serializers
from decimal import Decimal
from ..models import Goal, Account


class GoalSerializer(serializers.ModelSerializer):
    """
    Serializer for Goal model with progress tracking.
    """
    owner = serializers.StringRelatedField(read_only=True)
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)
    linked_account_name = serializers.CharField(source='linked_account.name', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    is_goal_reached = serializers.BooleanField(read_only=True)

    class Meta:
        model = Goal
        fields = [
            'id', 'name', 'description', 'goal_type', 'goal_type_display',
            'target_amount', 'current_amount', 'remaining_amount', 'progress_percentage',
            'target_date', 'linked_account', 'linked_account_name', 'is_active',
            'is_completed', 'is_goal_reached', 'completed_at', 'owner',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'is_completed', 'completed_at', 'created_at', 'updated_at'
        ]

    def validate_linked_account(self, value):
        """Validate linked account belongs to the current user if provided."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                if value.owner != request.user:
                    raise serializers.ValidationError("Linked account must belong to you.")
        return value

    def validate_target_amount(self, value):
        """Validate target amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Target amount must be positive.")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Target amount cannot exceed 999,999,999.99.")
        return value

    def validate_current_amount(self, value):
        """Validate current amount is not negative."""
        if value < 0:
            raise serializers.ValidationError("Current amount cannot be negative.")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Current amount cannot exceed 999,999,999.99.")
        return value

    def validate(self, attrs):
        """Validate goal consistency."""
        target_amount = attrs.get('target_amount')
        current_amount = attrs.get('current_amount')

        # If both are provided, validate current <= target for new goals
        if target_amount and current_amount:
            if current_amount > target_amount:
                # Allow this for debt payoff goals where current might be higher
                goal_type = attrs.get('goal_type')
                if goal_type != 'debt':
                    raise serializers.ValidationError(
                        "Current amount cannot exceed target amount."
                    )

        return attrs

    def create(self, validated_data):
        """Create goal with owner set to current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for goal creation with account ID.
    """
    linked_account_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Goal
        fields = [
            'name', 'description', 'goal_type', 'target_amount', 'current_amount',
            'target_date', 'linked_account_id', 'is_active'
        ]

    def validate_linked_account_id(self, value):
        """Validate linked account exists and belongs to user if provided."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    account = Account.objects.get(id=value, owner=request.user)
                    return value
                except Account.DoesNotExist:
                    raise serializers.ValidationError("Account not found or does not belong to you.")
        return value

    def validate_target_amount(self, value):
        """Validate target amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Target amount must be positive.")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Target amount cannot exceed 999,999,999.99.")
        return value

    def validate_current_amount(self, value):
        """Validate current amount is not negative."""
        if value < 0:
            raise serializers.ValidationError("Current amount cannot be negative.")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Current amount cannot exceed 999,999,999.99.")
        return value

    def create(self, validated_data):
        """Create goal with proper model relationships."""
        request = self.context.get('request')
        user = request.user

        # Convert account ID to model instance if provided
        linked_account_id = validated_data.pop('linked_account_id', None)
        linked_account = None
        if linked_account_id:
            linked_account = Account.objects.get(id=linked_account_id, owner=user)

        # Create goal
        goal = Goal.objects.create(
            owner=user,
            linked_account=linked_account,
            **validated_data
        )

        return goal


class GoalProgressUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating goal progress.
    """
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        """Validate amount change."""
        goal = self.context.get('goal')
        if goal:
            new_amount = goal.current_amount + value
            if new_amount < 0:
                raise serializers.ValidationError("Progress update would result in negative amount.")
            if new_amount > Decimal('999999999.99'):
                raise serializers.ValidationError("Progress update would exceed maximum amount.")
        return value

    def update_goal_progress(self, goal):
        """Update the goal's progress."""
        amount_change = self.validated_data['amount']
        new_amount = goal.current_amount + amount_change
        goal.update_progress(new_amount)
        return goal


class GoalSummarySerializer(serializers.Serializer):
    """
    Serializer for goal summary statistics.
    """
    total_goals = serializers.IntegerField()
    active_goals = serializers.IntegerField()
    completed_goals = serializers.IntegerField()
    total_target_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_saved_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_progress = serializers.FloatField()
    by_type = serializers.DictField()