from django.conf import settings
from django.db import models


class Post(models.Model):
    """Модель поста."""
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:50]

    @property
    def likes_count(self):
        """Количество лайков."""
        if hasattr(self, '_likes_count'):
            return self._likes_count
        return self.likes.count()

    @likes_count.setter
    def likes_count(self, value):
        self._likes_count = value

    @property
    def comments_count(self):
        """Количество комментариев."""
        if hasattr(self, '_comments_count'):
            return self._comments_count
        return self.comments.count()

    @comments_count.setter
    def comments_count(self, value):
        self._comments_count = value


class Comment(models.Model):
    """Модель комментария."""
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий {self.author.username} к посту {self.post.id}'


class Like(models.Model):
    """Модель лайка."""
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пост'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        'Дата',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                name='unique_like'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} лайкнул пост {self.post.id}'
