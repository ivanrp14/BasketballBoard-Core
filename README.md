# 🏀 Basketball Playbook API  

API para **crear, guardar y compartir jugadas de baloncesto** en equipos virtuales.  
Construida con **FastAPI**, utiliza **PostgreSQL** para usuarios, equipos y permisos, y **MongoDB** para almacenar las jugadas en formato JSON flexible.  

---

## 🚀 Funcionalidades principales
- 🔐 **Autenticación de usuarios** (registro/login con JWT).  
- 🏀 **Gestión de equipos**:  
  - Cada usuario puede crear **un único equipo**.  
  - Invitación a nuevos miembros mediante `invitation_code`.  
- 👥 **Roles y permisos**:  
  - **Admin** → gestiona equipo y jugadas.  
  - **Editor** → crea y modifica jugadas.  
  - **Viewer** → solo visualiza jugadas.  
- 📋 **Jugadas**:  
  - **Postgres** → metadata (id, nombre, equipo, fecha).  
  - **MongoDB** → contenido flexible (`data` en JSON).  
  - Acceso controlado según rol.  

---

## 🛠️ Tecnologías
- [FastAPI](https://fastapi.tiangolo.com/) – Framework backend.  
- [PostgreSQL](https://www.postgresql.org/) – Base de datos relacional.  
- [MongoDB](https://www.mongodb.com/) – Base de datos NoSQL para jugadas.  
- [SQLAlchemy](https://www.sqlalchemy.org/) – ORM para Postgres.  
- [Pydantic](https://docs.pydantic.dev/) – Validación de datos.  
- [Alembic](https://alembic.sqlalchemy.org/) – Migraciones de base de datos.  
- [Docker](https://www.docker.com/) – (opcional) para levantar servicios fácilmente.  

---

## 📂 Estructura del proyecto
