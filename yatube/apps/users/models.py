from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    
    email = models.EmailField(
        'Email',
        unique=True,
        help_text='Введите email адрес'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def followers_count(self):
        """Количество подписчиков."""
        if hasattr(self, '_followers_count'):
            return self._followers_count
        return self.following.count()

    @followers_count.setter
    def followers_count(self, value):
        self._followers_count = value

    @property
    def following_count(self):
        """Количество подписок."""
        if hasattr(self, '_following_count'):
            return self._following_count
        return self.follower.count()

    @following_count.setter
    def following_count(self, value):
        self._following_count = value


class Profile(models.Model):
    """Профиль пользователя."""
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        'О себе',
        max_length=500,
        blank=True
    )
    birth_date = models.DateField(
        'Дата рождения',
        blank=True,
        null=True
    )
    website = models.URLField(
        'Веб-сайт',
        max_length=200,
        blank=True
    )
    location = models.CharField(
        'Местоположение',
        max_length=100,
        blank=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'


class Follow(models.Model):
    """Модель подписок."""
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
