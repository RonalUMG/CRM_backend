# CRM Backend

Backend de practica para un CRM construido con Django y Django REST Framework.

## Stack
- Python
- Django
- Django REST Framework
- django-filter
- SQLite (desarrollo)

## Requisitos
- Python 3.12+ (o version compatible con tu entorno)
- Git

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
Windows PowerShell:
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
- Dashboard admin: `http://127.0.0.1:8000/admin/clients/client/dashboard/`

## Endpoints API
- `GET/POST /api/clients/`
- `GET/POST /api/leads/`
- `POST /api/leads/{id}/convert/`
- `GET/POST /api/products/`
- `GET/POST /api/opportunities/`

## Ejecutar pruebas
```bash
python manage.py test clients
```

## Notas
- El flujo de conversion de lead crea o reutiliza cliente por email.
- Si el lead no tiene telefono, `convert` responde `400` con mensaje claro.
