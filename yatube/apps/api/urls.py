from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='posts')
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'follow', views.FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_pk>/comments/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='comments-list'),
    path('posts/<int:post_pk>/comments/<int:pk>/', views.CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comments-detail'),
    path('token/', obtain_auth_token, name='token'),
]
