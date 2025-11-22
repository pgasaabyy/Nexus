from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True, null=True)
    carga_horaria = models.IntegerField()

    def __str__(self):
        return self.nome

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    ementa = models.TextField(blank=True, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='disciplinas')

    def __str__(self):
        return self.nome

class Turma(models.Model):
    TURNO_CHOICES = [('Manhã', 'Manhã'), ('Tarde', 'Tarde'), ('Noite', 'Noite'), ('Integral', 'Integral')]
    codigo = models.CharField(max_length=50)
    semestre = models.CharField(max_length=20)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.codigo} ({self.semestre})"

class Professor(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    especialidade = models.CharField(max_length=100, blank=True, null=True)
    data_admissao = models.DateField()

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class Matricula(models.Model):
    STATUS_CHOICES = [('Ativo', 'Ativo'), ('Trancado', 'Trancado'), ('Concluido', 'Concluido')]
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='registros')
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT)
    data_matricula = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ativo')

    def __str__(self):
        return f"{self.aluno} - {self.turma}"

class Nota(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    tipo_avaliacao = models.CharField(max_length=50)
    data_lancamento = models.DateField(default=timezone.now)

class Frequencia(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    data_aula = models.DateField()
    presente = models.BooleanField(default=False)
    justificativa = models.TextField(blank=True, null=True)