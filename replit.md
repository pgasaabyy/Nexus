# Nexus - Sistema de Gestão Escolar

## Project Overview
Nexus is a comprehensive school management system (Sistema de Gestão Escolar) developed for SENAI Morvan Figueiredo. It provides an integrated platform connecting administrators, secretariat, coordination, teachers, and students in a secure and scalable ecosystem.

## Technology Stack
- **Framework**: Django 5.2.8
- **Language**: Python 3.11
- **Database**: PostgreSQL (Replit managed)
- **Frontend**: HTML, CSS, JavaScript
- **Libraries**: 
  - Django REST Framework (API)
  - ReportLab (PDF generation)
  - Pillow (image handling)
  - Django Import/Export (data management)
  - psycopg2-binary (PostgreSQL adapter)

## Project Structure
```
nexus/
├── escola/                      # Main application
│   ├── models.py               # Data models (Aluno, Professor, Turma, etc.)
│   ├── views.py                # View controllers
│   ├── templates/escola/       # HTML templates with Django inheritance
│   │   ├── base_coordenacao.html   # Base template for coordination
│   │   ├── base_professor.html     # Base template for professors
│   │   ├── coor_*.html             # Coordination pages
│   │   ├── professor_*.html        # Professor pages
│   │   └── aluno_*.html            # Student pages
│   └── static/escola/          # CSS, JS, images
│       ├── css/aluno.css       # Main styling reference
│       └── js/                 # JavaScript files
├── nexus/                      # Project settings
│   ├── settings.py             # Configuration
│   └── urls.py                 # URL routing
├── manage.py                   # Django management script
└── run.sh                      # Server startup script (migrate + collectstatic + runserver)
```

## Recent Changes (December 2, 2025)
- Migrated from SQLite/MySQL to PostgreSQL (Replit managed database)
- Applied all database migrations successfully
- Converted templates to Django format with {% extends %} and {% block %}
- Created base templates for coordenação and professor roles
- Standardized CSS using aluno.css as reference
- Configured Django to run on 0.0.0.0:5000 for Replit's proxy
- Added CSRF_TRUSTED_ORIGINS for Replit domains
- Fixed Python 3.11 compatibility with psycopg2-binary
- run.sh now includes migration step before server start

## Key Features
- **Academic Management**: Student enrollment, class schedules, grades
- **Role-Based Access Control (RBAC)**: Admin, Secretariat, Coordination, Teachers, Students
- **Dashboards**: Customized views for each user type
- **API**: RESTful endpoints for data integration
- **Reports**: PDF and Excel export capabilities
- **Calendar & Events**: Academic calendar and event management

## User Roles
| Role | Permissions | URL Prefix |
|------|-------------|------------|
| Admin/Secretariat | Full access, manage enrollments, generate reports | /secretaria/ |
| Coordenação | Manage students, teachers, turmas, comunicados | /coordenacao/ |
| Professor | Manage classes, input grades, track attendance | /professor/ |
| Aluno (Student) | View grades, attendance, course materials | /aluno/ |

## Template Hierarchy
Templates use Django template inheritance for consistency:
- `base_coordenacao.html` - Base for all coordination pages
- `base_professor.html` - Base for all professor pages  
- All pages use `aluno.css` styling patterns

## Database Models
- **Aluno**: Student records
- **Professor**: Teacher records
- **Turma**: Class groups
- **Matricula**: Enrollments
- **Nota**: Grades
- **Frequencia**: Attendance
- **Aviso**: Announcements/Communications
- **Evento**: Calendar events

## Commands
- Start server: `bash run.sh`
- Manual start: `python3.11 manage.py runserver 0.0.0.0:5000`
- Run migrations: `python3.11 manage.py migrate`
- Create superuser: `python3.11 manage.py createsuperuser`
- Collect static: `python3.11 manage.py collectstatic`

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (set by Replit)
- `SECRET_KEY`: Django secret key

## Notes
- Uses Python 3.11 explicitly due to package compatibility
- Static files collected to /staticfiles/ for production
- Uses PostgreSQL with SSL in production
- All templates converted to Django format with proper inheritance
- CSS styling standardized based on aluno.css patterns
