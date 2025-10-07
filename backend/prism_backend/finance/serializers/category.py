from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with hierarchical support.
    """
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    full_name = serializers.CharField(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'full_name', 'category_type', 'category_type_display',
            'color', 'parent', 'parent_name', 'subcategories', 'is_active',
            'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_subcategories(self, obj):
        """Get subcategories for this category."""
        if hasattr(obj, 'subcategories'):
            subcategories = obj.subcategories.filter(is_active=True)
            return CategorySerializer(subcategories, many=True, context=self.context).data
        return []

    def validate_name(self, value):
        """Validate category name is unique within the same parent for the user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            parent = self.initial_data.get('parent')

            # Check if category with this name already exists for this user and parent
            existing = Category.objects.filter(owner=user, name=value, parent=parent)

            # Exclude current instance if updating
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                parent_name = parent.name if parent else "root level"
                raise serializers.ValidationError(
                    f"You already have a category named '{value}' in {parent_name}."
                )
        return value

    def validate_parent(self, value):
        """Validate parent category belongs to the same user."""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                if value.owner != request.user:
                    raise serializers.ValidationError("Parent category must belong to you.")

                # Prevent circular references
                if self.instance and value == self.instance:
                    raise serializers.ValidationError("Category cannot be its own parent.")

                # Check for circular reference in hierarchy
                current = value
                while current.parent:
                    if self.instance and current.parent == self.instance:
                        raise serializers.ValidationError(
                            "This would create a circular reference in the category hierarchy."
                        )
                    current = current.parent
        return value

    def validate_color(self, value):
        """Validate color is a valid hex color."""
        if not value.startswith('#'):
            raise serializers.ValidationError("Color must be a hex color starting with #.")
        if len(value) != 7:
            raise serializers.ValidationError("Color must be in format #RRGGBB.")
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError("Invalid hex color format.")
        return value

    def create(self, validated_data):
        """Create category with owner set to current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Serializer for category tree structure.
    """
    subcategories = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'full_name', 'category_type', 'category_type_display',
            'color', 'subcategories', 'is_active'
        ]

    def get_subcategories(self, obj):
        """Recursively get subcategories."""
        subcategories = obj.subcategories.filter(is_active=True)
        return CategoryTreeSerializer(subcategories, many=True, context=self.context).data