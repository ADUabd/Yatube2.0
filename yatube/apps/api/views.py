from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.posts.models import Post, Comment, Like
from apps.users.models import Follow
from .serializers import (
    PostSerializer,
    PostCreateSerializer,
    CommentSerializer,
    UserSerializer,
    FollowSerializer,
    FollowCreateSerializer
)

User = get_user_model()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Доступ только автору или только чтение."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постов."""
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Post.objects.select_related(
            'author',
            'author__profile'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Лайк/анлайк поста."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            return Response({
                'status': 'unliked',
                'likes_count': post.likes.count()
            })
        
        return Response({
            'status': 'liked',
            'likes_count': post.likes.count()
        })


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.filter(
            post_id=post_id
        ).select_related(
            'author',
            'author__profile'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для пользователей."""
    
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.select_related(
            'profile'
        ).annotate(
            followers_count=Count('following', distinct=True),
            following_count=Count('follower', distinct=True)
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Текущий пользователь."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class FollowViewSet(viewsets.ViewSet):
    """ViewSet для подписок."""
    
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Список подписок текущего пользователя."""
        follows = Follow.objects.filter(
            user=request.user
        ).select_related(
            'author',
            'author__profile'
        )
        serializer = FollowSerializer(follows, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Создание подписки."""
        serializer = FollowCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = serializer.validated_data['username']
        try:
            author = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': f'Пользователь {username} не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем дубликат подписки
        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'error': f'Вы уже подписаны на {author.username}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Follow.objects.create(user=request.user, author=author)
        
        return Response(
            {'status': f'Вы подписались на {author.username}'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        """Отписка."""
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Укажите username'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            author = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': f'Пользователь {username} не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        deleted, _ = Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
        
        if deleted:
            return Response(
                {'status': f'Вы отписались от {author.username}'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': f'Вы не были подписаны на {author.username}'},
            status=status.HTTP_400_BAD_REQUEST
        )
