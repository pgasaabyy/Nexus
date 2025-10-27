from django.db import models

# Create your models here.
from django.db import models
from core.models import Usuario

class DocumentoAluno(models.Model):
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='documentos/')
    data_envio = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_documento} - {self.aluno}"
