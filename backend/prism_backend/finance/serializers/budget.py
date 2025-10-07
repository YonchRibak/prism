from rest_framework import serializers
from decimal import Decimal
from ..models import Budget, Category


class BudgetSerializer(serializers.ModelSerializer):
    """
    Serializer for Budget model with spending tracking.
    """
    owner = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_full_name = serializers.CharField(source='category.full_name', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'category', 'category_name', 'category_full_name',
            'amount', 'period', 'period_display', 'start_date', 'end_date',
            'spent_amount', 'remaining_amount', 'percentage_used', 'is_over_budget',
            'is_active', 'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_category(self, value):
        """Validate category belongs to the current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.owner != request.user:
                raise serializers.ValidationError("Category must belong to you.")
        return value

    def validate_amount(self, value):
        """Validate budget amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be positive.")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Budget amount cannot exceed 999,999,999.99.")
        return value

    def validate(self, attrs):
        """Validate budget date range and overlaps."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        # Validate date range
        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError("End date must be after start date.")

        # Check for overlapping budgets for the same category
        if attrs.get('category') and start_date and end_date:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                user = request.user
                category = attrs['category']

                overlapping = Budget.objects.filter(
                    owner=user,
                    category=category,
                    is_active=True,
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )

                # Exclude current instance if updating
                if self.instance:
                    overlapping = overlapping.exclude(pk=self.instance.pk)

                if overlapping.exists():
                    raise serializers.ValidationError(
                        f"A budget for category '{category.name}' already exists for this time period."
                    )

        return attrs

    def create(self, validated_data):
        """Create budget with owner set to current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class BudgetCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for budget creation with category ID.
    """
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Budget
        fields = [
            'name', 'category_id', 'amount', 'period',
            'start_date', 'end_date', 'is_active'
        ]

    def validate_category_id(self, value):
        """Validate category exists and belongs to user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                category = Category.objects.get(id=value, owner=request.user)
                return value
            except Category.DoesNotExist:
                raise serializers.ValidationError("Category not found or does not belong to you.")
        return value

    def validate_amount(self, value):
        """Validate budget amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be positive.")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Budget amount cannot exceed 999,999,999.99.")
        return value

    def validate(self, attrs):
        """Validate budget date range."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError("End date must be after start date.")

        return attrs

    def create(self, validated_data):
        """Create budget with proper model relationships."""
        request = self.context.get('request')
        user = request.user

        # Convert category ID to model instance
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id, owner=user)

        # Create budget
        budget = Budget.objects.create(
            owner=user,
            category=category,
            **validated_data
        )

        return budget


class BudgetSummarySerializer(serializers.Serializer):
    """
    Serializer for budget summary statistics.
    """
    total_budgets = serializers.IntegerField()
    total_budget_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_remaining = serializers.DecimalField(max_digits=12, decimal_places=2)
    over_budget_count = serializers.IntegerField()
    on_track_count = serializers.IntegerField()