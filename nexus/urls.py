from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from escola.views import (
    # API e Gerais
    AlunoViewSet, NotaViewSet, home, login_view, logout_view,
    
    # Secretaria
    dashboard_secretaria, secretaria_alunos, secretaria_professores, 
    secretaria_academico, secretaria_documentos,
    
    # Coordenação
    dashboard_coordenacao, coordenacao_turmas, coordenacao_alunos,
    coordenacao_professores, coordenacao_relatorios, coordenacao_calendario,
    coordenacao_comunicados, coordenacao_configuracoes,
    
    # Professor
    dashboard_professor, professor_notas, professor_frequencia,
    professor_materiais, professor_calendario, professor_comunicados,
    professor_configuracoes,
    
    # Aluno
    dashboard_aluno
)

router = DefaultRouter()
router.register(r'alunos', AlunoViewSet)
router.register(r'notas', NotaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # --- ACESSO GERAL ---
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # --- SECRETARIA ---
    path('dashboard/secretaria/', dashboard_secretaria, name='dashboard_secretaria'),
    path('dashboard/secretaria/alunos/', secretaria_alunos, name='secretaria_alunos'),
    path('dashboard/secretaria/professores/', secretaria_professores, name='secretaria_professores'),
    path('dashboard/secretaria/academico/', secretaria_academico, name='secretaria_academico'),
    path('dashboard/secretaria/documentos/', secretaria_documentos, name='secretaria_documentos'),

    # --- COORDENAÇÃO ---
    path('dashboard/coordenacao/', dashboard_coordenacao, name='dashboard_coordenacao'),
    path('dashboard/coordenacao/turmas/', coordenacao_turmas, name='coordenacao_turmas'),
    path('dashboard/coordenacao/alunos/', coordenacao_alunos, name='coordenacao_alunos'),
    path('dashboard/coordenacao/professores/', coordenacao_professores, name='coordenacao_professores'),
    path('dashboard/coordenacao/relatorios/', coordenacao_relatorios, name='coordenacao_relatorios'),
    path('dashboard/coordenacao/calendario/', coordenacao_calendario, name='coordenacao_calendario'),
    path('dashboard/coordenacao/comunicados/', coordenacao_comunicados, name='coordenacao_comunicados'),
    path('dashboard/coordenacao/configuracoes/', coordenacao_configuracoes, name='coordenacao_configuracoes'),

    # --- PROFESSOR ---
    path('dashboard/professor/', dashboard_professor, name='dashboard_professor'),
    path('dashboard/professor/notas/', professor_notas, name='professor_notas'),
    path('dashboard/professor/frequencia/', professor_frequencia, name='professor_frequencia'),
    path('dashboard/professor/materiais/', professor_materiais, name='professor_materiais'),
    path('dashboard/professor/calendario/', professor_calendario, name='professor_calendario'),
    path('dashboard/professor/comunicados/', professor_comunicados, name='professor_comunicados'),
    path('dashboard/professor/configuracoes/', professor_configuracoes, name='professor_configuracoes'),

    # --- ALUNO ---
    path('dashboard/aluno/', dashboard_aluno, name='dashboard_aluno'),
]