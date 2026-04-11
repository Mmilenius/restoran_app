# Використовуємо офіційний образ Python (версія 3.10 підходить до твоєї)
FROM python:3.10-slim

# Налаштування змінного середовища (щоб Python не створював .pyc файли і логі виводилися одразу)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Створюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл залежностей і встановлюємо їх
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копіюємо весь проект у контейнер
COPY . /app/

# Відкриваємо порт 8000
EXPOSE 8000

# Команда для запуску сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]