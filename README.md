# YaMDb API

REST API для сбора отзывов пользователей на произведения (книги, фильмы, музыка).

## Технологии
- **Python 3.10+** + **Django 5.1** + **Django REST Framework**
- **JWT аутентификация** через Simple JWT
- **SQLite** (разработка) / **PostgreSQL** (продакшен)

## Функциональность
- Регистрация и аутентификация пользователей
- Ролевая модель (user/moderator/admin)
- CRUD операции с произведениями, категориями, жанрами
- Система отзывов и комментариев
- Рейтинговая система

## Быстрый старт
```bash
# Клонирование и установка зависимостей
git clone https://github.com/hawkxdev/api-yamdb.git
cd api-yamdb/api_yamdb
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Настройка и запуск
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Документация
- **Redoc:** http://127.0.0.1:8000/redoc/
- **Тестирование:** `pytest`
