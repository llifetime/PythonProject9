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