from django.db import models

# Create your models here.
from django.db import models
from core.models import Usuario

class Professor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='professor')
    disciplinas = models.CharField(max_length=200)
    formacao = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.usuario.get_full_name()
