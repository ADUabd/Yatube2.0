# Yatube 2.0

Социальная сеть для публикации личных записей.

## Функционал

- Регистрация и авторизация пользователей (по email)
- Профили пользователей с аватарками и биографией
- Создание, редактирование и удаление постов
- Загрузка изображений к постам
- Комментарии к постам
- Лайки постов
- Подписки на авторов
- Лента подписок
- Поиск по постам и авторам
- REST API

## Технологии

- Python 3.12
- Django 5.x
- SQLite (по умолчанию)
- Django REST Framework
- Bootstrap 5

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/yourusername/yatube.git
cd yatube
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать файл .env

```bash
cp .env.example .env
```

### 5. Применить миграции

```bash
python manage.py migrate
```

### 6. Создать суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Собрать статику (для продакшена)

```bash
python manage.py collectstatic
```

### 8. Запустить сервер разработки

```bash
python manage.py runserver
```

Сайт доступен по адресу: http://localhost:8000

## API

API доступно по адресу `/api/v1/`

### Эндпоинты:

- `GET /api/v1/posts/` - список постов
- `POST /api/v1/posts/` - создать пост
- `GET /api/v1/posts/{id}/` - получить пост
- `PUT /api/v1/posts/{id}/` - обновить пост
- `DELETE /api/v1/posts/{id}/` - удалить пост
- `POST /api/v1/posts/{id}/like/` - лайк/анлайк
- `GET /api/v1/posts/{id}/comments/` - комментарии к посту
- `POST /api/v1/posts/{id}/comments/` - добавить комментарий
- `GET /api/v1/users/` - список пользователей
- `GET /api/v1/users/me/` - текущий пользователь
- `GET /api/v1/follow/` - подписки
- `POST /api/v1/follow/` - подписаться
- `POST /api/v1/token/` - получить токен

## Структура проекта

```
yatube/
├── apps/
│   ├── api/         # REST API
│   ├── core/        # Базовые компоненты
│   ├── posts/       # Посты, комментарии, лайки
│   └── users/       # Пользователи, профили, подписки
├── config/          # Настройки Django
├── static/          # Статические файлы
├── templates/       # HTML шаблоны
├── manage.py
└── requirements.txt
```

## Тестирование

```bash
pytest
```

## Лицензия

MIT
