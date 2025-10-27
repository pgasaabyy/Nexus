from django.db import models

# Create your models here.
from django.db import models
from alunos.models import Aluno

class Desempenho(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.CharField(max_length=100)
    nota = models.DecimalField(max_digits=4, decimal_places=2)
    frequencia = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.aluno} - {self.disciplina}"
