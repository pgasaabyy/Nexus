# NEXUS - Sistema de Gestão Escolar

## Overview
NEXUS is a comprehensive school management system developed with Django 5.2 and PostgreSQL. It provides modules for Students, Teachers, Secretariat, and Coordination, featuring a responsive design and full CRUD (Create, Read, Update, Delete) functionalities. The system aims to streamline administrative tasks, academic management, and communication within an educational institution.

## User Preferences
- System should function responsively on all devices (desktop, tablet, mobile)
- Design following the NEXUS color palette
- Graphs and charts must be functional on all dashboards
- Groups must be created automatically with hierarchical permissions

## System Architecture

### UI/UX Decisions
The system adheres to a modern design aesthetic with a specific color palette:
- Primary Color: `#092F76` (dark blue)
- Secondary Color: `#8ED6D7` (pool blue)
- Accent Color: `#B1B7DC` (light blue)
- Background Color: `#EDEED9` (beige)
- Cards feature a `border-radius: 15px` and `box-shadow: 0 4px 15px rgba(0,0,0,0.08)`.
- Font: Poppins (Google Fonts).
- Buttons have `border-radius: 10px` and smooth transitions.
- Responsive CSS with breakpoints for tablet and mobile devices is implemented across all templates.
- Profile photo upload functionality is integrated for Aluno, Professor, Secretaria, and Coordenação roles.

### Technical Implementations & Feature Specifications
The project is structured with a main `escola/` app containing models, views, and templates. Custom management commands handle group creation and data population.

**Core Models:**
- `Curso`, `Disciplina`, `Turma`, `Sala`
- `Professor`, `Aluno`, `Matrícula`
- `Nota`, `Frequência`
- `Aviso` (with author, recipient, active status), `Evento`, `HorarioAula`, `Documento`
- `Material` (for educational material uploads)

**Role-Based Functionalities:**

*   **Aluno (Student):**
    *   View academic reports (boletim) and attendance (frequência).
    *   Export academic reports as PDF.
    *   View calendar and class schedules.
    *   Submit absence justifications.
    *   Profile and password settings.
*   **Professor (Teacher):**
    *   Record grades and attendance.
    *   Manage educational materials (upload/download/delete).
    *   Send announcements to classes.
    *   Manage calendar events.
    *   Profile and password settings.
*   **Secretaria (Secretariat):**
    *   Full CRUD for students, teachers, courses, classes, and subjects.
    *   Issue and manage documents, including file uploads and status tracking (PENDENTE, EMITIDO, ENTREGUE).
    *   View academic calendar.
    *   Profile and password settings.
*   **Coordenação (Coordination):**
    *   Full CRUD for classes, students, and teachers (with optional user creation).
    *   Manage calendar events (add/edit/delete).
    *   Send announcements to classes (with full CRUD).
    *   Generate detailed analytical reports with class filters and export options.
    *   Oversee teachers.
    *   Profile and password settings.

**Marketing/Institutional Pages:**
- `/institucional/` - About us page with company mission, vision, values, timeline, and team sections
- `/plataforma/` - Platform features, pricing plans, FAQ, and how-it-works sections
- `/juridico/` - Legal pages including Terms of Use, Privacy Policy, Cookie Policy, and LGPD compliance

**System Design Choices:**
- **Template Inheritance:** Extensive use of Django's template inheritance with base templates (`base_aluno.html`, `base_professor.html`, `base_secretaria.html`, `base_coordenacao.html`) for consistent UI and easier maintenance.
- **Atomic Transactions:** Critical operations, especially those involving user creation, grade submission, and professor assignments to classes/disciplines, utilize atomic transactions for data integrity and error handling with rollback capabilities.
- **Automated Group and Permission Management:** Custom management commands (`criar_grupos.py`) automatically set up hierarchical permission groups (Secretaria, Coordenação, Professor, Aluno) upon system initialization, ensuring granular access control.
- **Dynamic Content:** Dashboards feature dynamic content such as performance charts in `aluno_boletim.html` and `aluno_dashboard.html`, and dynamic calendars in `secre_calendario.html`.
- **Modals for CRUD:** Many CRUD operations, especially for Coordination and Secretariat roles, are implemented using modal dialogs for an improved user experience.
- **Credential Management:** New user creation (e.g., for students or professors) includes explicit username and password fields with pre-validation for uniqueness and non-empty passwords.

### System Hierarchy
```
nexus/              # Django project configurations
escola/             # Main app with models, views, templates
  ├── management/   # Custom management commands
  │   └── commands/
  │       ├── criar_grupos.py        # Creates hierarchical groups and permissions
  │       └── criar_dados_completos.py # Populates database with test data
  ├── static/       # CSS, JS, images
  ├── templates/    # HTML templates with inheritance
  └── urls.py       # Routes organized by function
```

## External Dependencies
- **Django 5.2.8**: Web framework.
- **djangorestframework**: For building Web APIs.
- **psycopg2-binary**: PostgreSQL database adapter.
- **reportlab**: For generating PDF reports (e.g., student academic reports).
- **openpyxl**: For reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files.
- **django-filter**: For simple filtering of querysets.
- **django-crispy-forms**: For elegant display of Django forms.
- **django-import-export**: For importing and exporting data.
- **gunicorn**: WSGI HTTP Server for UNIX (production deployment).
- **whitenoise**: For serving static files efficiently in production.