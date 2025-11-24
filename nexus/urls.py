from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from escola.views import AlunoViewSet, NotaViewSet, home, login_view, dashboard_secretaria, dashboard_professor, dashboard_aluno

# Rotas da API
router = DefaultRouter()
router.register(r'alunos', AlunoViewSet)
router.register(r'notas', NotaViewSet)

urlpatterns = [
    # Painel Admin do Django
    path('admin/', admin.site.urls),
    
    # API (Gráficos)
    path('api/', include(router.urls)),

    # Site (HTML)
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    
    # Dashboards
    path('dashboard/secretaria/', dashboard_secretaria, name='dashboard_secretaria'),
    path('dashboard/professor/', dashboard_professor, name='dashboard_professor'),
    path('dashboard/aluno/', dashboard_aluno, name='dashboard_aluno'),
]