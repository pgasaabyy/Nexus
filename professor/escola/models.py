from django.db import models
from django.contrib.auth.models import User

class Escola(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    cnpj = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    ano_letivo = models.IntegerField()
    bimestre_atual = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Escolas"
    
    def __str__(self):
        return self.nome

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.IntegerField()
    professores = models.ManyToManyField(User)
    
    def __str__(self):
        return self.nome

class Aluno(models.Model):
    nome = models.CharField(max_length=255)
    matricula = models.CharField(max_length=100, unique=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='alunos')
    frequencia = models.FloatField(default=100.0)
    
    def __str__(self):
        return self.nome

class Nota(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.CharField(max_length=100)
    bimestre = models.IntegerField()
    nota = models.FloatField()
    observacoes = models.TextField(blank=True)
    data_lancamento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina}"

class Comunicado(models.Model):
    assunto = models.CharField(max_length=255)
    destinatario = models.CharField(max_length=255)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Comunicados"
    
    def __str__(self):
        return self.assunto

class Material(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='materiais/')
    data_envio = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.titulo

class Evento(models.Model):
    titulo = models.CharField(max_length=255)
    data = models.DateField()
    descricao = models.TextField()
    tipo = models.CharField(max_length=50, choices=[
        ('prova', 'Prova'),
        ('reuniao', 'Reunião'),
        ('trabalho', 'Trabalho'),
        ('evento', 'Evento'),
        ('outro', 'Outro'),
    ])
    
    class Meta:
        verbose_name_plural = "Eventos"
    
    def __str__(self):
        return self.titulo
