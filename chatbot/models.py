from django.db import models

class Interacao(models.Model):
    pergunta = models.TextField()
    resposta = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pergunta: {self.pergunta[:40]}..."
