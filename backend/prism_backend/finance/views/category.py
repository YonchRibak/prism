from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import Category
from ..serializers import CategorySerializer, CategoryTreeSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transaction categories.
    All categories are scoped to the authenticated user.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category_type', 'is_active', 'parent']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    search_fields = ['name']

    def get_queryset(self):
        """Return categories for the authenticated user only"""
        return Category.objects.filter(owner=self.request.user)

    def destroy(self, request, pk=None):
        """Delete a category with validation"""
        try:
            category = self.get_object()

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
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        serializer = CategoryTreeSerializer(parent_categories, many=True, context={'request': request})

        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get categories grouped by type (income/expense)"""
        queryset = self.get_queryset().filter(is_active=True)

        income_categories = queryset.filter(category_type='income')
        expense_categories = queryset.filter(category_type='expense')

        income_serializer = CategorySerializer(income_categories, many=True, context={'request': request})
        expense_serializer = CategorySerializer(expense_categories, many=True, context={'request': request})

        return Response({
            'income': {
                'count': len(income_serializer.data),
                'categories': income_serializer.data
            },
            'expense': {
                'count': len(expense_serializer.data),
                'categories': expense_serializer.data
            }
        })