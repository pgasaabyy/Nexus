from django.contrib import admin
from .models import Turma, Aluno, Professor, Comunicado, EventoCalendario

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turno', 'professor', 'alunos_matriculados', 'media_turma', 'ativa')
    list_filter = ('turno', 'ativa')
    search_fields = ('nome',)


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome', 'turma', 'media', 'frequencia', 'status')
    list_filter = ('status', 'turma')
    search_fields = ('nome', 'matricula')


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'disciplina', 'carga_horaria')
    search_fields = ('usuario__first_name', 'disciplina')


@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'destinatario', 'criado_em', 'enviado')
    list_filter = ('destinatario', 'enviado')
    search_fields = ('titulo',)


@admin.register(EventoCalendario)
class EventoCalendarioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data')
    search_fields = ('titulo',)
