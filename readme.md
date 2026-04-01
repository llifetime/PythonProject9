# Django Learning Platform

## Установка и запуск
1. Клонируйте репозиторий
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте: `venv\Scripts\activate` (Windows)
4. Установите зависимости: `pip install -r requirements.txt`
5. Примените миграции: `python manage.py migrate`
6. Загрузите фикстуры: `python manage.py loaddata all_data.json`
7. Запустите сервер: `python manage.py runserver`

## API эндпоинты
- Регистрация: POST /api/users/register/
- Авторизация: POST /api/users/token/
- Курсы: GET /api/materials/courses/
- Платежи: GET /api/users/payments/
- Профиль: GET /api/users/profile/

## Тестовые пользователи
- Админ: admin@example.com / admin123
- Модератор: moderator@example.com / moderator123
- Студент: student@example.com / student123


# Проект PythonProject9

## Настройка сервера
- Сервер: Ubuntu 22.04 LTS
- Python 3.11
- PostgreSQL
- Nginx
- Gunicorn + Supervisor

## CI/CD
При push в ветки main/master:
1. Запускаются тесты
2. При успехе - деплой на сервер 158.160.236.174

## Переменные окружения
Скопируйте `.env.example` в `.env` и заполните значения.

## Локальный запуск
```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver