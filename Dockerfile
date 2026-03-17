# Dockerfile
FROM python:3.14-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements
COPY requirements.txt .
COPY requirements_dev.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn psycopg2-binary

# Копируем проект
COPY . .

# Создаем директории для статических и медиа файлов
RUN mkdir -p /app/static /app/media

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]