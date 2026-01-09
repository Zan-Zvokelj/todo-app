# FastAPI Todo Application

A backend Todo application with user authentication, admin dashboard,
and analytics endpoints, designed to demonstrate real-world backend architecture,
database migrations, and containerized deployment.


## Project Highlights

- Clean layered FastAPI architecture
- Database schema versioning with Alembic
- Optimized PostgreSQL queries with indexes
- Dockerized local development environment
- Production-style authentication and authorization flow


A production-ready **FastAPI backend application** built with:
- PostgreSQL
- SQLAlchemy
- Alembic migrations
- Docker & Docker Compose
- JWT authentication
- Automated tests

This project was built as a portfolio project to demonstrate real-world backend development practices.

---

##  Features

- FastAPI REST API
- PostgreSQL database
- SQLAlchemy ORM
- Alembic database migrations
- JWT authentication & role-based access
- Dockerized application (API + DB)
- Automated tests with pytest
- Admin & user routes
- Health check endpoint

---


## Deployment

This application is deployed using:
- Docker
- Render (Web Service)
- Neon PostgreSQL (cloud database)

Environment variables are used for all sensitive configuration.

### Environment Variables

Required variables:
- DATABASE_URL
- SECRET_KEY
- ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES

The database uses PostgreSQL with SQLAlchemy and Alembic migrations.

## Run with Docker (recommended)

### Requirements
- Docker
- Docker Compose

### Start the application
```bash
docker compose up --build


---

This project was built for learning and portfolio purposes and follows
best practices commonly used in production backend systems.
