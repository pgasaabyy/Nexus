from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User


class Curso(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True, null=True)
    carga_horaria = models.IntegerField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    ementa = models.TextField(blank=True, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='disciplinas')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"


class Turma(models.Model):
    TURNO_CHOICES = [
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
        ('Noite', 'Noite'),
        ('Integral', 'Integral')
    ]
    codigo = models.CharField(max_length=50)
    semestre = models.CharField(max_length=20)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.codigo} ({self.semestre})"

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"


class Professor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='perfil_professor'
    )
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    especialidade = models.CharField(max_length=100, blank=True, null=True)
    data_admissao = models.DateField()
    disciplinas = models.ManyToManyField(
        'Disciplina',
        blank=True,
        related_name='professores'
    )
    turmas = models.ManyToManyField(
        Turma,
        blank=True,
        related_name='professores'
    )
    foto = models.ImageField(upload_to='professores_fotos/', blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"


class Aviso(models.Model):
    DESTINATARIO_CHOICES = [
        ('todos', 'Todos'),
        ('alunos', 'Alunos'),
        ('professores', 'Professores'),
        ('turma', 'Turma Específica'),
    ]
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, null=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='avisos_criados')
    destinatario = models.CharField(max_length=20, choices=DESTINATARIO_CHOICES, default='todos')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        ordering = ['-data_criacao']


class Aluno(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='perfil_aluno'
    )
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    turma_atual = models.ForeignKey(
        Turma,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alunos_turma'
    )
    foto = models.ImageField(upload_to='alunos_fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

    def calcular_media_geral(self):
        notas = Nota.objects.filter(matricula__aluno=self)
        if not notas.exists():
            return 0
        soma = sum([float(n.valor) for n in notas])
        return round(soma / len(notas), 1)

    def contar_faltas(self):
        return Frequencia.objects.filter(matricula__aluno=self, presente=False).count()

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"


class Matricula(models.Model):
    STATUS_CHOICES = [
        ('Ativo', 'Ativo'),
        ('Trancado', 'Trancado'),
        ('Concluido', 'Concluído')
    ]
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='registros')
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT)
    data_matricula = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ativo')

    def __str__(self):
        return f"{self.aluno} - {self.turma}"

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"


class Nota(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    valor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    tipo_avaliacao = models.CharField(max_length=50)
    data_lancamento = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.valor} - {self.disciplina}"

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"


class Frequencia(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    data_aula = models.DateField()
    presente = models.BooleanField(default=False)
    justificativa = models.TextField(blank=True, null=True)

    def __str__(self):
        status = "Presente" if self.presente else "Falta"
        return f"{self.data_aula} - {status}"

    class Meta:
        verbose_name = "Frequência"
        verbose_name_plural = "Frequências"
        unique_together = ['matricula', 'disciplina', 'data_aula']


class Evento(models.Model):
    TIPO_CHOICES = [
        ('feriado', 'Feriado'),
        ('prova', 'Prova'),
        ('trabalho', 'Entrega de Trabalho'),
        ('evento', 'Evento Escolar'),
        ('reuniao', 'Reunião'),
    ]
    titulo = models.CharField(max_length=200)
    data = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.data})"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['data']


class HorarioAula(models.Model):
    DIA_SEMANA_CHOICES = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
    ]
    
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='horarios')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=DIA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        ordering = ['hora_inicio', 'dia_semana']
        verbose_name = "Horário de Aula"
        verbose_name_plural = "Horários de Aula"

    def __str__(self):
        return f"{self.turma} - {self.get_dia_semana_display()} - {self.hora_inicio}"


class Documento(models.Model):
    TIPOS_CHOICES = [
        ('DECLARACAO_MATRICULA', 'Declaração de Matrícula'),
        ('HISTORICO', 'Histórico Escolar'),
        ('ATESTADO_FREQUENCIA', 'Atestado de Frequência'),
        ('OUTRO', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EMITIDO', 'Emitido'),
        ('ENTREGUE', 'Entregue'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=50, choices=TIPOS_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_emissao = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    arquivo = models.FileField(upload_to='documentos/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.aluno.nome}"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-data_solicitacao']


class Material(models.Model):
    TIPO_CHOICES = [
        ('apostila', 'Apostila'),
        ('exercicio', 'Lista de Exercícios'),
        ('slides', 'Slides/Apresentação'),
        ('video', 'Vídeo'),
        ('outro', 'Outro'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to='materiais/')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='outro')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='materiais')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, null=True, blank=True, related_name='materiais')
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='materiais')
    data_upload = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} - {self.disciplina.nome}"

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"
        ordering = ['-data_upload']


class Sala(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField(default=40)
    tipo = models.CharField(max_length=50, default='Sala de Aula')
    bloco = models.CharField(max_length=50, blank=True, null=True)
    recursos = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"


class JustificativaFalta(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='justificativas')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    justificativa = models.TextField()
    documento = models.FileField(upload_to='justificativas/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_analise = models.DateTimeField(blank=True, null=True)
    analisado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='justificativas_analisadas')
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Justificativa - {self.aluno.nome} ({self.data_inicio} a {self.data_fim})"

    class Meta:
        verbose_name = "Justificativa de Falta"
        verbose_name_plural = "Justificativas de Faltas"
        ordering = ['-data_solicitacao']
