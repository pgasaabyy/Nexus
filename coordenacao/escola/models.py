from django.db import models
from django.contrib.auth.models import User

class Turma(models.Model):
    TURNO_CHOICES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('noturno', 'Noturno'),
    ]
    
    nome = models.CharField(max_length=100)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES)
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    alunos_matriculados = models.IntegerField(default=0)
    media_turma = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    frequencia = models.IntegerField(default=0)
    ativa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
    
    def __str__(self):
        return self.nome


class Aluno(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]
    
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=200)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True)
    media = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    frequencia = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
    
    def __str__(self):
        return self.nome


class Professor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    disciplina = models.CharField(max_length=100)
    turmas = models.ManyToManyField(Turma)
    carga_horaria = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
    
    def __str__(self):
        return self.usuario.get_full_name()


class Comunicado(models.Model):
    DESTINATARIO_CHOICES = [
        ('alunos', 'Alunos'),
        ('professores', 'Professores'),
        ('secretaria', 'Secretaria'),
        ('pais', 'Pais/Responsáveis'),
    ]
    
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    destinatario = models.CharField(max_length=20, choices=DESTINATARIO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)
    enviado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Comunicado'
        verbose_name_plural = 'Comunicados'
    
    def __str__(self):
        return self.titulo


class EventoCalendario(models.Model):
    titulo = models.CharField(max_length=200)
    data = models.DateTimeField()
    descricao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
    
    def __str__(self):
        return self.titulo
