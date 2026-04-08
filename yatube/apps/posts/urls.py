from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная и лента
    path('', views.IndexView.as_view(), name='index'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    
    # CRUD постов
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Лайки
    path('post/<int:pk>/like/', views.LikeView.as_view(), name='like'),
    
    # Комментарии
    path('post/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment_create'),
    path('post/<int:pk>/comment/<int:comment_pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    
    # Поиск
    path('search/', views.SearchView.as_view(), name='search'),
]
