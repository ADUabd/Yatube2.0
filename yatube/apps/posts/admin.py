from django.contrib import admin

from .models import Post, Comment, Like


class CommentInline(admin.TabularInline):
    """Инлайн для комментариев в админке поста."""
    model = Comment
    extra = 0
    raw_id_fields = ('author',)


class LikeInline(admin.TabularInline):
    """Инлайн для лайков в админке поста."""
    model = Like
    extra = 0
    raw_id_fields = ('user',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка для постов."""
    
    list_display = (
        'id',
        'author',
        'text_preview',
        'image',
        'likes_count',
        'comments_count',
        'created_at'
    )
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    inlines = [CommentInline, LikeInline]

    @admin.display(description='Текст')
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text

    @admin.display(description='Лайков')
    def likes_count(self, obj):
        return obj.likes.count()

    @admin.display(description='Комментариев')
    def comments_count(self, obj):
        return obj.comments.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев."""
    
    list_display = ('id', 'post', 'author', 'text_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username')
    raw_id_fields = ('post', 'author')

    @admin.display(description='Текст')
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Админка для лайков."""
    
    list_display = ('id', 'post', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    raw_id_fields = ('post', 'user')
