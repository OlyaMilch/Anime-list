# Python version
FROM python:3.13

# Рабочая директория внутри контейнера ( место, куда ты потом копируешь файлы с помощью COPY)
WORKDIR /app

# Project files copied to container
COPY requirements.txt .
COPY main.py .
COPY anime_parser.py .
COPY fetch_anime.py .
COPY README.md .
COPY .gitignore .
# Copy all files in folder
COPY templates/ templates/

# Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Launching a Flask application (this launch is used if Dockerfile is in the project folder)
CMD ["python", "main.py"]
