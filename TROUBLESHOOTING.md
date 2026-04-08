# Решение проблемы: AttributeError при setattr в queryset

## Возможные причины ошибки

Ошибка `setattr(obj, attr_name, row[col_pos])` при итерации queryset обычно возникает когда:

1. **Несоответствие между полями модели и структурой БД** - поле удалено из модели, но осталось в БД
2. **Поле является свойством (@property), но Django пытается установить его как обычное поле**
3. **Некорректная работа select_related/prefetch_related**
4. **Проблема с миграциями** - не все миграции применены

## Шаги для исправления

### 1. Запустите диагностику
```bash
cd /home/adu/Documents/b_D2oMvTUR6p7/yatube
python manage.py shell < diagnose.py
```

### 2. Проверьте и примените миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Удалите cache Django
```bash
python manage.py clear_cache
```

### 4. Проверьте целостность БД
```bash
python manage.py check
```

## Возможное решение: Пересоздание БД

Если проблема не решается, попробуйте пересоздать БД:

```bash
# 1. Удалите БД
rm db.sqlite3

# 2. Создайте новую БД с миграциями
python manage.py migrate

# 3. Создайте суперпользователя (опционально)
python manage.py createsuperuser

# 4. Соберите static файлы
python manage.py collectstatic --noinput
```

## Сделанные исправления

Я исправил следующие проблемы в коде:

### 1. **CustomLogoutView** - добавлено `next_page`
```python
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('posts:index')
```

### 2. **Формы валидации** - исправлена обработка текста
- В `clean_text()` методах больше не стриируется текст перед возвратом
- Возвращается оригинальное значение, только проверяется что оно не пустое

### 3. **PostCreateView** - упрощен (удалены дополнительные проверки)
- Теперь полагается на валидацию в форме

### 4. **API сериализаторы** - исправлены методы валидации
- Больше не стриируется текст перед возвратом из `validate_text()`

## Проверка после исправления

После применения этих изменений проверьте:

```bash
# Откройте оболочку Django
python manage.py shell

# Выполните следующие команды
from apps.posts.models import Post
from django.db.models import Count

# Попробуйте загрузить несколько постов
posts = Post.objects.select_related('author', 'author__profile').annotate(
    likes_count=Count('likes', distinct=True)
)[:5]

for post in posts:
    print(f"Post {post.id}: {post.text[:50]}")
```

## Если ошибка все еще присутствует

1. Предоставьте полный traceback из Django Debug Toolbar
2. Укажите точный URL, который вызывает ошибку
3. Укажите название поля, которое не удается установить

## Быстрая диагностика

Если при открытии главной страницы (`/`) возникает ошибка:

```bash
python manage.py shell

from apps.posts.views import IndexView
view = IndexView()
view.request = type('Request', (), {'user': None})()

# Попробуйте загрузить queryset напрямую
from apps.posts.models import Post
from django.db.models import Count

qs = Post.objects.select_related('author', 'author__profile').prefetch_related(
    'comments', 'likes'
).annotate(
    likes_count=Count('likes', distinct=True),
    comments_count=Count('comments', distinct=True)
).order_by('-created_at')

print(f"Queryset count: {qs.count()}")
for post in qs[:1]:
    print(f"Пост: {post}")
```
