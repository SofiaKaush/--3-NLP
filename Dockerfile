# Используем легковесный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все скрипты приложения (app_v1.py - app_v4.py) и остальные файлы
COPY . .

# Открываем порт для самого продвинутого приложения (v4)
EXPOSE 5004

# Указываем команду запуска по умолчанию
CMD ["python", "app_v4.py"]