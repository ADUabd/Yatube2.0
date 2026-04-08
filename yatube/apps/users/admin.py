from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Profile, Follow


class ProfileInline(admin.StackedInline):
    """Инлайн для профиля в админке пользователя."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админка для кастомного пользователя."""
    
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined'
    )
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [ProfileInline]
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('username', 'first_name', 'last_name')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Админка для профилей."""
    
    list_display = ('user', 'location', 'created_at')
    search_fields = ('user__username', 'user__email', 'location')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка для подписок."""
    
    list_display = ('user', 'author', 'created_at')
    search_fields = ('user__username', 'author__username')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'author')
