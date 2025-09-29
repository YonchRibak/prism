from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import Category


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transaction categories.
    All categories are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category_type', 'is_active', 'parent']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    search_fields = ['name']

    def get_queryset(self):
        """Return categories for the authenticated user only"""
        return Category.objects.filter(owner=self.request.user)

    def get_serializer_data(self, instance):
        """Convert category instance to serializer data"""
        return {
            'id': instance.id,
            'name': instance.name,
            'full_name': instance.full_name,
            'category_type': instance.category_type,
            'category_type_display': instance.get_category_type_display(),
            'color': instance.color,
            'parent': {
                'id': instance.parent.id,
                'name': instance.parent.name
            } if instance.parent else None,
            'is_active': instance.is_active,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }

    def list(self, request):
        """List all user categories"""
        queryset = self.filter_queryset(self.get_queryset())
        categories = [self.get_serializer_data(category) for category in queryset]

        return Response({
            'count': len(categories),
            'results': categories
        })

    def retrieve(self, request, pk=None):
        """Get a specific category"""
        try:
            category = self.get_queryset().get(pk=pk)
            return Response(self.get_serializer_data(category))
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """Create a new category"""
        try:
            data = request.data

            # Validate required fields
            if not data.get('name'):
                return Response(
                    {'error': 'name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle parent category
            parent = None
            if data.get('parent_id'):
                try:
                    parent = self.get_queryset().get(pk=data['parent_id'])
                except Category.DoesNotExist:
                    return Response(
                        {'error': 'Parent category not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Check for duplicate name within same parent
            if Category.objects.filter(
                owner=request.user,
                name=data['name'],
                parent=parent
            ).exists():
                return Response(
                    {'error': 'Category with this name already exists in this parent'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create category
            category = Category.objects.create(
                owner=request.user,
                name=data['name'],
                category_type=data.get('category_type', 'expense'),
                color=data.get('color', '#6B7280'),
                parent=parent,
                is_active=data.get('is_active', True)
            )

            return Response(
                self.get_serializer_data(category),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Update a category"""
        try:
            category = self.get_queryset().get(pk=pk)
            data = request.data

            # Handle parent category change
            if 'parent_id' in data:
                parent = None
                if data['parent_id']:
                    try:
                        parent = self.get_queryset().get(pk=data['parent_id'])
                        # Prevent circular reference
                        if parent == category or category in parent.get_ancestors():
                            return Response(
                                {'error': 'Cannot set parent that would create circular reference'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    except Category.DoesNotExist:
                        return Response(
                            {'error': 'Parent category not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )

                category.parent = parent

            # Update other fields
            updatable_fields = ['name', 'category_type', 'color', 'is_active']

            for field in updatable_fields:
                if field in data:
                    if field == 'name':
                        # Check for duplicate name within same parent
                        if (data[field] != category.name and
                            Category.objects.filter(
                                owner=request.user,
                                name=data[field],
                                parent=category.parent
                            ).exists()):
                            return Response(
                                {'error': 'Category with this name already exists in this parent'},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                    setattr(category, field, data[field])

            category.save()

            return Response(self.get_serializer_data(category))

        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Delete a category"""
        try:
            category = self.get_queryset().get(pk=pk)

            # Check if category has transactions
            if category.transactions.exists():
                return Response(
                    {'error': 'Cannot delete category with existing transactions'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if category has subcategories
            if category.subcategories.exists():
                return Response(
                    {'error': 'Cannot delete category with subcategories'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category.delete()

            return Response(
                {'message': 'Category deleted successfully'},
                status=status.HTTP_200_OK
            )

        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get categories organized as a tree structure"""
        queryset = self.get_queryset().filter(is_active=True)

        # Get parent categories
        parent_categories = queryset.filter(parent__isnull=True)

        def build_tree(category):
            category_data = self.get_serializer_data(category)
            subcategories = queryset.filter(parent=category)
            if subcategories:
                category_data['subcategories'] = [build_tree(sub) for sub in subcategories]
            return category_data

        tree = [build_tree(cat) for cat in parent_categories]

        return Response({
            'count': len(tree),
            'results': tree
        })

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get categories grouped by type (income/expense)"""
        queryset = self.get_queryset().filter(is_active=True)

        income_categories = [
            self.get_serializer_data(cat)
            for cat in queryset.filter(category_type='income')
        ]
        expense_categories = [
            self.get_serializer_data(cat)
            for cat in queryset.filter(category_type='expense')
        ]

        return Response({
            'income': {
                'count': len(income_categories),
                'categories': income_categories
            },
            'expense': {
                'count': len(expense_categories),
                'categories': expense_categories
            }
        })