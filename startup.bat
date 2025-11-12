@echo off

docker-compose -f docker/docker-compose.yml up -d
start "" cmd /k "call .venv\Scripts\activate.bat && python manage.py runserver"
cd frontend
npm start