from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    path('', views.dashboard_professor, name='dashboard'),
    path('lancamento-notas/', views.lancamento_notas, name='lancamento_notas'),
    path('frequencia/', views.frequencia, name='frequencia'),
    path('materiais/', views.materiais, name='materiais'),
    path('calendario/', views.calendario, name='calendario'),
    path('comunicados/', views.comunicados, name='comunicados'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]
