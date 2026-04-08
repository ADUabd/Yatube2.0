from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.posts.models import Post, Comment, Like
from apps.users.models import Profile, Follow

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля."""
    
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'location', 'website')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    
    profile = ProfileSerializer(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile',
            'followers_count',
            'following_count',
            'posts_count',
            'date_joined'
        )
        read_only_fields = ('email', 'date_joined')

    def get_posts_count(self, obj):
        return obj.posts.count()


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""
    
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'created_at')
        read_only_fields = ('author', 'created_at')
    
    def validate_text(self, value):
        """Проверка что комментарий не пуст."""
        if not value or not value.strip():
            raise serializers.ValidationError('Комментарий не может быть пустым.')
        return value


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор поста."""
    
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'text',
            'image',
            'likes_count',
            'comments_count',
            'is_liked',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('author', 'created_at', 'updated_at')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания поста."""
    
    class Meta:
        model = Post
        fields = ('text', 'image')
    
    def validate_text(self, value):
        """Проверка что текст поста не пуст."""
        if not value or not value.strip():
            raise serializers.ValidationError('Текст поста не может быть пустым.')
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Текст поста должен содержать минимум 3 символа.')
        return value


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    
    user = UserSerializer(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author', 'created_at')
        read_only_fields = ('user', 'created_at')


class FollowCreateSerializer(serializers.Serializer):
    """Сериализатор создания подписки."""
    
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден.')
        
        request = self.context.get('request')
        if request.user == user:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        
        if Follow.objects.filter(user=request.user, author=user).exists():
            raise serializers.ValidationError('Вы уже подписаны на этого пользователя.')
        
        return value
