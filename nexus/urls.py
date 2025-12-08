from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from escola.views import AlunoViewSet, NotaViewSet

router = DefaultRouter()
router.register(r'alunos', AlunoViewSet)
router.register(r'notas', NotaViewSet)

def health_check(request):
    return JsonResponse({"status": "healthy"}, status=200)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('escola.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
