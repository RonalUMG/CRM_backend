# CRM Backend

Backend de practica para un CRM universitario con Django + DRF.

## Stack
- Python
- Django
- Django REST Framework
- JWT (`djangorestframework-simplejwt`)
- django-filter
- SQLite (desarrollo)

## Modulos de negocio (admin)
- `academics`: Campus y Sitios
- `admissions`: Leads y Correos
- `commercial`: Productos y Oportunidades
- `crm`: Clientes, Notas y dashboard global

## Instalacion local
1. Clonar repositorio:
```bash
git clone https://github.com/RonalUMG/CRM_backend.git
cd CRM_backend
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
```
PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```
Git Bash:
```bash
source venv/Scripts/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
- Copia `.env.example` a `.env` y ajusta valores reales.

5. Migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Levantar servidor:
```bash
python manage.py runserver
```

## Rutas principales
- Admin: `http://127.0.0.1:8000/admin/`
- API base: `http://127.0.0.1:8000/api/`

Dashboards admin:
- CRM: `http://127.0.0.1:8000/admin/crm/client/dashboard/`
- Estructura: `http://127.0.0.1:8000/admin/academics/campus/dashboard/`
- Admisiones: `http://127.0.0.1:8000/admin/admissions/lead/dashboard/`
- Comercial: `http://127.0.0.1:8000/admin/commercial/product/dashboard/`

## Endpoints API
- `GET/POST /api/clients/`
- `GET/POST /api/leads/`
- `POST /api/leads/{id}/convert/`
- `GET/POST /api/products/`
- `GET/POST /api/opportunities/`

JWT:
- `POST /api/token/`
- `POST /api/token/refresh/`

## Ejecutar pruebas
```bash
python manage.py test clients
```

## Notas
- La API esta protegida con JWT (`IsAuthenticated`).
- El flujo `convert` crea o reutiliza cliente por email.
- Si un lead no tiene telefono, `convert` responde `400`.
