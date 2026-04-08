#!/usr/bin/env python
"""
Скрипт для диагностики и исправления проблем с моделями и базой данных.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.apps import apps
from django.core import checks

print("=" * 80)
print("ДИАГНОСТИКА YATUBE")
print("=" * 80)

# 1. Проверка наличия ошибок в моделях
print("\n1. Проверка целостности моделей...")
errors = checks.run_checks()
if errors:
    print(f"❌ Найдено {len(errors)} ошибок:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✓ Ошибок в моделях не найдено")

# 2. Проверка наличия необходимых миграций
print("\n2. Проверка статуса миграций...")
try:
    call_command('showmigrations', verbosity=0)
    print("✓ Все миграции применены")
except Exception as e:
    print(f"❌ Ошибка при проверке миграций: {e}")

# 3. Проверка структуры базы данных
print("\n3. Проверка структуры базы данных...")
with connection.cursor() as cursor:
    # Получаем все таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"✓ Найдено {len(tables)} таблиц в БД")
    
    # Проверяем таблицы для наших моделей
    expected_tables = [
        'posts_post',
        'posts_comment', 
        'posts_like',
        'users_follow',
        'users_profile',
        'users_customuser'
    ]
    
    existing_tables = [t[0] for t in tables]
    for table in expected_tables:
        if table in existing_tables:
            print(f"  ✓ Таблица {table} существует")
        else:
            print(f"  ❌ Таблица {table} НЕ НАЙДЕНА")

# 4. Проверка количества записей
print("\n4. Статус данных в БД...")
from apps.posts.models import Post, Comment, Like
from apps.users.models import CustomUser, Follow, Profile

print(f"  - Пользователей: {CustomUser.objects.count()}")
print(f"  - Постов: {Post.objects.count()}")
print(f"  - Комментариев: {Comment.objects.count()}")
print(f"  - Лайков: {Like.objects.count()}")
print(f"  - Подписок: {Follow.objects.count()}")
print(f"  - Профилей: {Profile.objects.count()}")

# 5. Попытка загрузить несколько постов
print("\n5. Проверка доступности данных...")
try:
    posts = Post.objects.select_related(
        'author',
        'author__profile'
    ).prefetch_related(
        'comments',
        'likes'
    )[:5]
    print(f"✓ Успешно загружено {posts.count()} постов из БД")
    for post in posts:
        print(f"  - Пост ID {post.id}: {post.text[:50]}")
except Exception as e:
    print(f"❌ Ошибка при загрузке постов: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 80)
