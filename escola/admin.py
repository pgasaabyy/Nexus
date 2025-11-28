from django.contrib import admin
from .models import Aluno, Turma, Disciplina, Professor, Aviso, Nota, Frequencia, Matricula, Curso

# Isso faz as tabelas aparecerem no painel /admin
admin.site.register(Aluno)
admin.site.register(Turma)
admin.site.register(Disciplina)
admin.site.register(Professor)
admin.site.register(Aviso)
admin.site.register(Nota)
admin.site.register(Frequencia)
admin.site.register(Matricula)
admin.site.register(Curso)