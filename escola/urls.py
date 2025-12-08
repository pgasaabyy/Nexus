from django.urls import path
from . import views

urlpatterns = [
    # Home e Autenticação
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard Aluno (mantém compatibilidade com rotas originais)
    path('dashboard/aluno/', views.dashboard_aluno, name='dashboard_aluno'),
    path('dashboard/aluno/boletim/', views.aluno_boletim, name='aluno_boletim'),
    path('dashboard/aluno/boletim/pdf/', views.exportar_boletim_pdf, name='exportar_boletim_pdf'),
    path('dashboard/aluno/horario/', views.aluno_horario, name='aluno_horario'),
    path('dashboard/aluno/frequencia/', views.aluno_frequencia, name='aluno_frequencia'),
    path('dashboard/aluno/frequencia/pdf/', views.exportar_frequencia_pdf, name='exportar_frequencia_pdf'),
    path('dashboard/aluno/frequencia/excel/', views.exportar_frequencia_excel, name='exportar_frequencia_excel'),
    path('dashboard/aluno/calendario/', views.aluno_calendario, name='aluno_calendario'),
    path('dashboard/aluno/configuracoes/', views.aluno_configuracoes, name='aluno_configuracoes'),
    path('dashboard/aluno/justificativa/', views.aluno_justificativa, name='aluno_justificativa'),
    path('dashboard/aluno/evento/', views.aluno_evento, name='aluno_evento'),

    # Dashboard Professor
    path('dashboard/professor/', views.dashboard_professor, name='dashboard_professor'),
    path('dashboard/professor/notas/', views.professor_notas, name='professor_notas'),
    path('dashboard/professor/notas/salvar/', views.professor_salvar_notas, name='professor_salvar_notas'),
    path('dashboard/professor/frequencia/', views.professor_frequencia, name='professor_frequencia'),
    path('dashboard/professor/frequencia/salvar/', views.professor_salvar_frequencia, name='professor_salvar_frequencia'),
    path('dashboard/professor/materiais/', views.professor_materiais, name='professor_materiais'),
    path('dashboard/professor/materiais/download/<int:material_id>/', views.download_material, name='download_material'),
    path('dashboard/professor/calendario/', views.professor_calendario, name='professor_calendario'),
    path('dashboard/professor/comunicados/', views.professor_comunicados, name='professor_comunicados'),
    path('dashboard/professor/configuracoes/', views.professor_configuracoes, name='professor_configuracoes'),

    # Dashboard Secretaria
    path('dashboard/secretaria/', views.dashboard_secretaria, name='dashboard_secretaria'),
    path('dashboard/secretaria/alunos/', views.secretaria_alunos, name='secretaria_alunos'),
    path('dashboard/secretaria/alunos/adicionar/', views.secretaria_aluno_adicionar, name='secretaria_aluno_adicionar'),
    path('dashboard/secretaria/alunos/<int:aluno_id>/editar/', views.secretaria_aluno_editar, name='secretaria_aluno_editar'),
    path('dashboard/secretaria/alunos/<int:aluno_id>/excluir/', views.secretaria_aluno_excluir, name='secretaria_aluno_excluir'),
    path('dashboard/secretaria/professores/', views.secretaria_professores, name='secretaria_professores'),
    path('dashboard/secretaria/academico/', views.secretaria_academico, name='secretaria_academico'),
    path('dashboard/secretaria/documentos/', views.secretaria_documentos, name='secretaria_documentos'),
    path('dashboard/secretaria/calendario/', views.secretaria_calendario, name='secretaria_calendario'),
    path('dashboard/secretaria/configuracoes/', views.secretaria_configuracoes, name='secretaria_configuracoes'),

    # Dashboard Coordenação
    path('dashboard/coordenacao/', views.dashboard_coordenacao, name='dashboard_coordenacao'),
    path('dashboard/coordenacao/turmas/', views.coordenacao_turmas, name='coordenacao_turmas'),
    path('dashboard/coordenacao/alunos/', views.coordenacao_alunos, name='coordenacao_alunos'),
    path('dashboard/coordenacao/professores/', views.coordenacao_professores, name='coordenacao_professores'),
    path('dashboard/coordenacao/relatorios/', views.coordenacao_relatorios, name='coordenacao_relatorios'),
    path('dashboard/coordenacao/calendario/', views.coordenacao_calendario, name='coordenacao_calendario'),
    path('dashboard/coordenacao/calendario/evento/adicionar/', views.coordenacao_evento_adicionar, name='coordenacao_evento_adicionar'),
    path('dashboard/coordenacao/calendario/evento/<int:evento_id>/editar/', views.coordenacao_evento_editar, name='coordenacao_evento_editar'),
    path('dashboard/coordenacao/calendario/evento/<int:evento_id>/excluir/', views.coordenacao_evento_excluir, name='coordenacao_evento_excluir'),
    path('dashboard/coordenacao/comunicados/', views.coordenacao_comunicados, name='coordenacao_comunicados'),
    path('dashboard/coordenacao/configuracoes/', views.coordenacao_configuracoes, name='coordenacao_configuracoes'),
    
    # Coordenação - Gestão de Turmas e Alunos
    path('dashboard/coordenacao/turmas/adicionar/', views.coordenacao_turma_adicionar, name='coordenacao_turma_adicionar'),
    path('dashboard/coordenacao/turmas/<int:turma_id>/editar/', views.coordenacao_turma_editar, name='coordenacao_turma_editar'),
    path('dashboard/coordenacao/turmas/<int:turma_id>/excluir/', views.coordenacao_turma_excluir, name='coordenacao_turma_excluir'),
    path('dashboard/coordenacao/alunos/adicionar/', views.coordenacao_aluno_adicionar, name='coordenacao_aluno_adicionar'),
    path('dashboard/coordenacao/alunos/<int:aluno_id>/editar/', views.coordenacao_aluno_editar, name='coordenacao_aluno_editar'),
    path('dashboard/coordenacao/alunos/<int:aluno_id>/excluir/', views.coordenacao_aluno_excluir, name='coordenacao_aluno_excluir'),
    
    # Coordenação - Gestão de Professores
    path('dashboard/coordenacao/professores/adicionar/', views.coordenacao_professor_adicionar, name='coordenacao_professor_adicionar'),
    path('dashboard/coordenacao/professores/<int:professor_id>/editar/', views.coordenacao_professor_editar, name='coordenacao_professor_editar'),
    path('dashboard/coordenacao/professores/<int:professor_id>/excluir/', views.coordenacao_professor_excluir, name='coordenacao_professor_excluir'),
]
