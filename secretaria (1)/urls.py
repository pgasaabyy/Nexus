from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Alunos
    path('alunos/', views.alunos_lista, name='alunos'),
    path('alunos/criar/', views.aluno_criar, name='aluno_criar'),
    path('alunos/<int:pk>/editar/', views.aluno_editar, name='aluno_editar'),
    path('alunos/<int:pk>/', views.aluno_detalhe, name='aluno_detalhe'),
    path('alunos/<int:pk>/documentos/', views.aluno_documentos, name='aluno_documentos'),
    
    # Professores
    path('professores/', views.professores_lista, name='professores'),
    path('professores/criar/', views.professor_criar, name='professor_criar'),
    path('professores/<int:pk>/editar/', views.professor_editar, name='professor_editar'),
    path('professores/<int:pk>/', views.professor_detalhe, name='professor_detalhe'),
    path('professores/<int:pk>/documentos/', views.professor_documentos, name='professor_documentos'),
    
    # Acadêmico
    path('academico/', views.academico, name='academico'),
    path('academico/cursos/criar/', views.curso_criar, name='curso_criar'),
    path('academico/cursos/<int:pk>/editar/', views.curso_editar, name='curso_editar'),
    path('academico/turmas/<int:pk>/editar/', views.turma_editar, name='turma_editar'),
    path('academico/disciplinas/<int:pk>/editar/', views.disciplina_editar, name='disciplina_editar'),
    
    # Documentos
    path('documentos/', views.documentos_lista, name='documentos'),
    path('documentos/<int:pk>/download/', views.documento_download, name='documento_download'),
    path('documentos/<int:pk>/visualizar/', views.documento_visualizar, name='documento_visualizar'),
    path('documentos/modelos/<int:pk>/download/', views.modelo_download, name='modelo_download'),
    path('documentos/modelos/<int:pk>/visualizar/', views.modelo_visualizar, name='modelo_visualizar'),
    
    # Outras páginas
    path('calendario/', views.calendario, name='calendario'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('tarefas/', views.tarefas, name='tarefas'),
]
