from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path
from django.urls import reverse_lazy

from . import views

app_name = 'users'

urlpatterns = [
    # Аутентификация
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Профиль
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),
    
    # Подписки
    path('profile/<str:username>/follow/', views.FollowView.as_view(), name='follow'),
    path('profile/<str:username>/unfollow/', views.UnfollowView.as_view(), name='unfollow'),
    path('profile/<str:username>/followers/', views.FollowersListView.as_view(), name='followers'),
    path('profile/<str:username>/following/', views.FollowingListView.as_view(), name='following'),
    
    # Смена пароля
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change.html',
            success_url=reverse_lazy('users:password_change_done')
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    
    # Сброс пароля
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
