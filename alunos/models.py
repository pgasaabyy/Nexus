from django.db import models

# Create your models here.
from django.db import models
from core.models import Usuario

class Aluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='aluno')
    matricula = models.CharField(max_length=20, unique=True)
    turma = models.CharField(max_length=50)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    responsavel = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.turma}"
