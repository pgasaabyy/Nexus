from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('alunos/', views.gestao_alunos, name='gestao_alunos'),
    path('professores/', views.gestao_professores, name='gestao_professores'),
    path('turmas/', views.gestao_turmas, name='gestao_turmas'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('calendario/', views.calendario, name='calendario'),
    path('comunicados/', views.comunicados, name='comunicados'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]
