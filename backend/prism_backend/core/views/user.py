from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from ..models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get current user profile information.
    """
    user = request.user

    return Response({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'created_at': user.created_at,
        'updated_at': user.updated_at,
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user profile information.
    """
    try:
        user = request.user
        data = request.data

        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'email']

        for field in updatable_fields:
            if field in data:
                # Check if email is already taken by another user
                if field == 'email' and data[field] != user.email:
                    if User.objects.filter(email=data[field]).exclude(id=user.id).exists():
                        return Response(
                            {'error': 'Email is already taken'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                setattr(user, field, data[field])

        user.save()

        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'updated_at': user.updated_at,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    """
    try:
        user = request.user
        data = request.data

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Validate required fields
        if not all([current_password, new_password, confirm_password]):
            return Response(
                {'error': 'All password fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify current password
        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check password confirmation
        if new_password != confirm_password:
            return Response(
                {'error': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        user.set_password(new_password)
        user.save()

        # Update session hash to prevent logout
        update_session_auth_hash(request, user)

        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    Delete user account and all associated data.
    """
    try:
        password = request.data.get('password')

        if not password:
            return Response(
                {'error': 'Password is required to delete account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify password
        if not request.user.check_password(password):
            return Response(
                {'error': 'Password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete user account (cascades to all related data)
        request.user.delete()

        return Response(
            {'message': 'Account deleted successfully'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )