#!/usr/bin/env python
"""
Скрипт для воспроизведения и проверки конкретной ошибки setattr
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.posts.views import IndexView, PostDetailView
from apps.posts.models import Post
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

print("=" * 80)
print("ПРОВЕРКА ОШИБКИ setattr")
print("=" * 80)

# Создаем mock request
factory = RequestFactory()
request = factory.get('/')

# Добавляем пользователя в request
request.user = User.objects.first()  # или AnonymousUser()

print(f"\n1. Проверка главной страницы...")
try:
    view = IndexView.as_view()
    response = view(request)
    print(f"✓ Главная страница загружается успешно")
    print(f"  Статус: {response.status_code}")
except Exception as e:
    print(f"❌ Ошибка при загрузке главной страницы:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n2. Прямая проверка queryset...")
try:
    # Пытаемся загрузить посты так же как делает IndexView
    qs = Post.objects.select_related(
        'author',
        'author__profile'
    ).prefetch_related(
        'comments',
        'likes'
    ).annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-created_at')
    
    posts = list(qs[:5])  # Конвертируем в список
    print(f"✓ Queryset работает успешно")
    print(f"  Загружено постов: {len(posts)}")
    
    for post in posts:
        print(f"  - Пост {post.id}: {post.text[:30]}...")
        
except Exception as e:
    print(f"❌ Ошибка при загрузке queryset:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n3. Проверка отдельного поста...")
try:
    post = Post.objects.first()
    if post:
        print(f"✓ Пост загружен успешно")
        print(f"  ID: {post.id}")
        print(f"  Автор: {post.author.username}")
        print(f"  Текст: {post.text[:50]}...")
    else:
        print(f"⚠ В БД нет постов")
except Exception as e:
    print(f"❌ Ошибка при загрузке поста:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n4. Проверка модели Post...")
try:
    from django.core.checks import run_checks
    errors = run_checks()
    
    if errors:
        print(f"❌ Найдено ошибок в моделях: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"✓ Модели проходят все проверки")
except Exception as e:
    print(f"❌ Ошибка при проверке моделей:")
    print(f"  {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 80)

# Если ошибка все еще возникает, выводим полезные команды
print("\nЕсли проблема не решена, попробуйте:")
print("  1. python manage.py migrate")
print("  2. python manage.py check")
print("  3. rm db.sqlite3 && python manage.py migrate")
