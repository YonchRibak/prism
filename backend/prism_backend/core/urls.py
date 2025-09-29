from django.urls import path
from .views import auth, user

app_name = 'core'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth.register, name='register'),
    path('auth/login/', auth.login, name='login'),
    path('auth/refresh/', auth.refresh_token, name='refresh_token'),

    # User profile endpoints
    path('user/profile/', user.profile, name='profile'),
    path('user/profile/update/', user.update_profile, name='update_profile'),
    path('user/change-password/', user.change_password, name='change_password'),
    path('user/delete-account/', user.delete_account, name='delete_account'),
]