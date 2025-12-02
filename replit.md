# Nexus - Sistema de Gestão Escolar

## Project Overview
Nexus is a comprehensive school management system (Sistema de Gestão Escolar) developed for SENAI Morvan Figueiredo. It provides an integrated platform connecting administrators, secretariat, teachers, and students in a secure and scalable ecosystem.

## Technology Stack
- **Framework**: Django 5.2.8
- **Language**: Python 3.11
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS, JavaScript
- **Libraries**: 
  - Django REST Framework (API)
  - ReportLab (PDF generation)
  - Pillow (image handling)
  - Django Import/Export (data management)

## Project Structure
```
nexus/
├── escola/              # Main application
│   ├── models.py       # Data models (Aluno, Professor, Turma, etc.)
│   ├── views.py        # View controllers
│   ├── templates/      # HTML templates
│   └── static/         # CSS, JS, images
├── nexus/              # Project settings
│   ├── settings.py     # Configuration
│   └── urls.py         # URL routing
├── manage.py           # Django management script
└── run.sh             # Server startup script
```

## Recent Changes (December 2, 2025)
- Converted from MySQL to SQLite for Replit compatibility
- Configured Django to run on 0.0.0.0:5000 for Replit's proxy
- Added CSRF_TRUSTED_ORIGINS for Replit domains
- Set up media file handling
- Configured deployment with autoscale target
- Fixed Python 3.11/3.12 compatibility issues

## Key Features
- **Academic Management**: Student enrollment, class schedules, grades
- **Role-Based Access Control (RBAC)**: Admin, Secretariat, Teachers, Students
- **Dashboards**: Customized views for each user type
- **API**: RESTful endpoints for data integration
- **Reports**: PDF and Excel export capabilities
- **Calendar & Events**: Academic calendar and event management

## Development Setup
The project is configured to run in Replit with:
- Python 3.11 for package compatibility
- Port 5000 for web preview
- SQLite for development database
- Static files served from /static/ and /media/

## User Roles
| Role | Permissions |
|------|-------------|
| Admin/Secretariat | Full access, manage enrollments, generate reports |
| Professor | Manage classes, input grades, track attendance |
| Aluno (Student) | View grades, attendance, course materials |

## Commands
- Start server: `bash run.sh` or `python3.11 manage.py runserver 0.0.0.0:5000`
- Run migrations: `python3.11 manage.py migrate`
- Create superuser: `python3.11 manage.py createsuperuser`
- Collect static: `python3.11 manage.py collectstatic`

## Notes
- Uses Python 3.11 explicitly due to package compatibility
- Static files path includes both nexus/static and escola/static
- Media uploads stored in /media directory
- Database migrations are complete and up to date
