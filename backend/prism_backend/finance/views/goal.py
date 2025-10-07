from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from datetime import datetime
from decimal import Decimal
from ..models import Goal
from ..serializers import GoalSerializer, GoalCreateSerializer, GoalProgressUpdateSerializer, GoalSummarySerializer


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial goals.
    All goals are scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['goal_type', 'is_active', 'is_completed', 'linked_account']
    ordering_fields = ['name', 'target_amount', 'target_date', 'created_at']
    ordering = ['-created_at']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Return goals for the authenticated user only"""
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return GoalCreateSerializer
        return GoalSerializer

    def create(self, request, *args, **kwargs):
        """Create goal with proper serializer"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save()
            # Return with the full serializer for response
            response_serializer = GoalSerializer(goal, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update goal progress by adding/subtracting amount"""
        try:
            goal = self.get_object()
            serializer = GoalProgressUpdateSerializer(
                data=request.data,
                context={'goal': goal, 'request': request}
            )

            if serializer.is_valid():
                updated_goal = serializer.update_goal_progress(goal)
                response_serializer = GoalSerializer(updated_goal, context={'request': request})
                return Response(response_serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Goal.DoesNotExist:
            return Response(
                {'error': 'Goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active goals"""
        queryset = self.get_queryset().filter(is_active=True, is_completed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed goals"""
        queryset = self.get_queryset().filter(is_completed=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def near_target(self, request):
        """Get goals that are close to their target (>80% progress)"""
        goals = []
        for goal in self.get_queryset().filter(is_active=True, is_completed=False):
            if goal.progress_percentage >= 80:
                goals.append(goal)

        serializer = self.get_serializer(goals, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get goal summary statistics"""
        queryset = self.get_queryset()

        total_goals = queryset.count()
        active_goals = queryset.filter(is_active=True, is_completed=False).count()
        completed_goals = queryset.filter(is_completed=True).count()

        total_target_amount = sum(goal.target_amount for goal in queryset.filter(is_active=True))
        total_saved_amount = sum(goal.current_amount for goal in queryset.filter(is_active=True))

        # Goals by type
        goal_types = {}
        for goal in queryset:
            goal_type = goal.goal_type
            if goal_type not in goal_types:
                goal_types[goal_type] = {'count': 0, 'target_amount': Decimal('0.00'), 'saved_amount': Decimal('0.00')}
            goal_types[goal_type]['count'] += 1
            goal_types[goal_type]['target_amount'] += goal.target_amount
            goal_types[goal_type]['saved_amount'] += goal.current_amount

        summary_data = {
            'total_goals': total_goals,
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'total_target_amount': total_target_amount,
            'total_saved_amount': total_saved_amount,
            'total_remaining_amount': total_target_amount - total_saved_amount,
            'average_progress': round(
                (total_saved_amount / total_target_amount * 100) if total_target_amount > 0 else 0,
                2
            ),
            'by_type': {k: {
                'count': v['count'],
                'target_amount': str(v['target_amount']),
                'saved_amount': str(v['saved_amount'])
            } for k, v in goal_types.items()}
        }

        serializer = GoalSummarySerializer(summary_data)
        return Response(serializer.data)