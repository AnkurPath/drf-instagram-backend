### Social networking application using Django Rest Framework

1. Clone the repository:

```
git clone https://github.com/AnkurPath/social-networking-app-drf.git

```
2. Create Virtual Environment:
```
python -m venv [Your Virtual Environment Name]
```
3. Move to `backend` folder directory:
```
cd backend
```
4. Install Required Modules:

```
pip install -r requirements.txt  
```
5. Make Migrations:
```
python manage.py makemigrations
manage.py migrate   
```

5. Start the server:
```
python manage.py runserver  
```
5. You will this in Terminal:
```
......\backend> python manage.py runserver     
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 04, 2024 - 22:10:19
Django version 5.0.6, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.

```

- Your server is started now you can use apis
- Postman collection is available in repository

### Note
- I will add Docker file currently i am Learning Docker
