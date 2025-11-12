# Базовый образ Python
FROM python:3.11

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt requirements.txt

# Обновление pip и установка зависимостей
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копирование исходного кода приложения
COPY mysite .
