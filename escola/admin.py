from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils import timezone
from .models import (
    Aluno, Turma, Disciplina, Professor, Aviso, 
    Nota, Frequencia, Matricula, Curso, Evento, HorarioAula, Documento,
    Material, Sala
)


class NexusAdminSite(AdminSite):
    site_header = 'NEXUS - Sistema de Gestão Escolar'
    site_title = 'NEXUS Admin'
    index_title = 'Painel de Controle'
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_alunos'] = Aluno.objects.count()
        extra_context['total_professores'] = Professor.objects.count()
        extra_context['total_turmas'] = Turma.objects.count()
        extra_context['total_cursos'] = Curso.objects.count()
        extra_context['total_eventos'] = Evento.objects.count()
        extra_context['documentos_pendentes'] = Documento.objects.filter(status='PENDENTE').count()
        extra_context['ultimos_alunos'] = Aluno.objects.select_related('turma_atual').order_by('-id')[:5]
        extra_context['ultimos_avisos'] = Aviso.objects.order_by('-data_criacao')[:5]
        extra_context['proximos_eventos'] = Evento.objects.filter(data__gte=timezone.now().date()).order_by('data')[:5]
        return super().index(request, extra_context=extra_context)


admin_site = NexusAdminSite(name='nexus_admin')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['matricula', 'nome', 'email', 'turma_atual', 'cpf']
    list_filter = ['turma_atual', 'turma_atual__curso']
    search_fields = ['nome', 'matricula', 'email', 'cpf']
    list_per_page = 25
    ordering = ['nome']
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'cpf', 'data_nascimento', 'email', 'telefone', 'foto')
        }),
        ('Dados Acadêmicos', {
            'fields': ('matricula', 'turma_atual')
        }),
        ('Acesso ao Sistema', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'especialidade', 'data_admissao', 'telefone']
    list_filter = ['especialidade', 'data_admissao', 'turmas', 'disciplinas']
    search_fields = ['nome', 'email', 'especialidade']
    list_per_page = 25
    ordering = ['nome']
    filter_horizontal = ('disciplinas', 'turmas')
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'email', 'telefone')
        }),
        ('Dados Profissionais', {
            'fields': ('especialidade', 'data_admissao')
        }),
        ('Turmas e Disciplinas', {
            'fields': ('disciplinas', 'turmas'),
            'description': 'Selecione as disciplinas e turmas que este professor leciona.'
        }),
        ('Acesso ao Sistema', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'curso', 'semestre', 'turno', 'get_total_alunos']
    list_filter = ['curso', 'turno', 'semestre']
    search_fields = ['codigo', 'curso__nome']
    list_per_page = 25
    
    def get_total_alunos(self, obj):
        return obj.alunos_turma.count()
    get_total_alunos.short_description = 'Total de Alunos'


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'carga_horaria', 'get_total_turmas']
    search_fields = ['nome', 'codigo']
    list_per_page = 25
    
    def get_total_turmas(self, obj):
        return obj.turma_set.count()
    get_total_turmas.short_description = 'Total de Turmas'


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso']
    list_filter = ['curso']
    search_fields = ['nome', 'curso__nome']
    list_per_page = 25


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'destinatario', 'turma', 'ativo', 'data_criacao']
    list_filter = ['destinatario', 'ativo', 'turma', 'data_criacao']
    search_fields = ['titulo', 'conteudo']
    list_per_page = 25
    ordering = ['-data_criacao']
    
    fieldsets = (
        (None, {
            'fields': ('titulo', 'conteudo', 'ativo')
        }),
        ('Destinatário', {
            'fields': ('destinatario', 'turma'),
            'description': 'Selecione o tipo de destinatário. Turma específica só funciona se selecionar "Turma Específica".'
        }),
        ('Autor', {
            'fields': ('autor',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data', 'tipo', 'turma']
    list_filter = ['tipo', 'data', 'turma']
    search_fields = ['titulo', 'descricao']
    list_per_page = 25
    ordering = ['data']
    date_hierarchy = 'data'


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ['get_aluno', 'disciplina', 'valor', 'tipo_avaliacao', 'data_lancamento']
    list_filter = ['disciplina', 'tipo_avaliacao', 'data_lancamento']
    search_fields = ['matricula__aluno__nome', 'disciplina__nome']
    list_per_page = 25
    ordering = ['-data_lancamento']
    
    def get_aluno(self, obj):
        return obj.matricula.aluno.nome
    get_aluno.short_description = 'Aluno'


@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ['get_aluno', 'disciplina', 'data_aula', 'presente']
    list_filter = ['presente', 'disciplina', 'data_aula']
    search_fields = ['matricula__aluno__nome']
    list_per_page = 25
    ordering = ['-data_aula']
    
    def get_aluno(self, obj):
        return obj.matricula.aluno.nome
    get_aluno.short_description = 'Aluno'


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'turma', 'data_matricula', 'status']
    list_filter = ['status', 'turma', 'data_matricula']
    search_fields = ['aluno__nome', 'turma__codigo']
    list_per_page = 25
    ordering = ['-data_matricula']


@admin.register(HorarioAula)
class HorarioAulaAdmin(admin.ModelAdmin):
    list_display = ['turma', 'disciplina', 'dia_semana', 'hora_inicio', 'hora_fim']
    list_filter = ['turma', 'disciplina', 'dia_semana']
    search_fields = ['turma__codigo', 'disciplina__nome']
    list_per_page = 25
    ordering = ['turma', 'dia_semana', 'hora_inicio']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'tipo', 'status', 'data_solicitacao', 'data_emissao']
    list_filter = ['tipo', 'status', 'data_solicitacao']
    search_fields = ['aluno__nome', 'descricao']
    list_per_page = 25
    ordering = ['-data_solicitacao']
    readonly_fields = ['data_solicitacao']
    
    fieldsets = (
        ('Documento', {
            'fields': ('aluno', 'tipo', 'descricao')
        }),
        ('Status', {
            'fields': ('status', 'data_solicitacao', 'data_emissao')
        }),
        ('Responsável', {
            'fields': ('criado_por',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'disciplina', 'professor', 'turma', 'ativo', 'data_upload']
    list_filter = ['tipo', 'disciplina', 'professor', 'ativo', 'data_upload']
    search_fields = ['titulo', 'descricao', 'professor__nome', 'disciplina__nome']
    list_per_page = 25
    ordering = ['-data_upload']
    
    fieldsets = (
        ('Material', {
            'fields': ('titulo', 'descricao', 'arquivo', 'tipo', 'ativo')
        }),
        ('Vinculação', {
            'fields': ('disciplina', 'turma', 'professor')
        }),
    )


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'capacidade', 'bloco']
    list_filter = ['tipo', 'bloco']
    search_fields = ['nome', 'bloco']
    list_per_page = 25
    ordering = ['nome']
