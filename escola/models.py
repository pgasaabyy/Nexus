from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User  # Importação essencial!

# --- CURSOS E DISCIPLINAS ---
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

# --- ESTRUTURA ---
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

# --- AVISOS (NOVO) ---
class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titulo

# --- ALUNOS ---
class Aluno(models.Model):
    # Relacionamento com o usuário do Django (Login)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='perfil_aluno')
    
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    
    # Campo para vincular o aluno a uma turma atual (facilita o dashboard)
    turma_atual = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos_turma')
    foto = models.ImageField(upload_to='alunos_fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

    # Métodos Inteligentes para o Dashboard
    def calcular_media_geral(self):
        # Busca todas as notas através das matrículas do aluno
        notas = Nota.objects.filter(matricula__aluno=self)
        if not notas.exists():
            return 0
        soma = sum([n.valor for n in notas])
        return round(soma / len(notas), 1)

    def contar_faltas(self):
        # Busca todas as faltas através das matrículas do aluno
        return Frequencia.objects.filter(matricula__aluno=self, presente=False).count()

# --- VÍNCULOS E DADOS ACADÊMICOS ---
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

    def __str__(self):
        return f"{self.valor} - {self.disciplina}"

class Frequencia(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    data_aula = models.DateField()
    presente = models.BooleanField(default=False)
    justificativa = models.TextField(blank=True, null=True)

    def __str__(self):
        status = "Presente" if self.presente else "Falta"
        return f"{self.data_aula} - {status}"