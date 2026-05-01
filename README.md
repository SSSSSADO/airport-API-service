# ✈️ Airport API Service

A REST API service for managing an airport system, including airports, airplanes, flights, and ticket orders.

Built with Django REST Framework, PostgreSQL, and Docker.

---

## Tech Stack

- Python 3.12+
- Django 6
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- Swagger / OpenAPI (drf-spectacular or drf-yasg)

---

## Access Points
- API Base URL: http://127.0.0.1:8000/api/
- Admin Panel: http://127.0.0.1:8000/admin/
- Swagger UI: http://127.0.0.1:8000/swagger/

## Project Setup (Docker)

### 1. Clone repository
```bash id="c1k9qp"
git clone <your-repo-url>
cd airport_API_service
docker compose up --build
docker exec -it django_app python manage.py migrate
docker exec -it django_app python manage.py createsuperuser
