from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPOS_USUARIO = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
        ('coordenacao', 'Coordenação'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.tipo})"
