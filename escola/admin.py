from django.contrib import admin
from .models import Aluno, Turma, Disciplina, Professor, Aviso, Nota, Frequencia, Matricula, Curso
from .models import Evento # Adicione Evento na importação
admin.site.register(Evento)

# Adicione HorarioAula na lista de imports
from .models import (
    Aluno, Turma, Disciplina, Professor, Aviso, 
    Nota, Frequencia, Matricula, Curso, Evento, HorarioAula
)

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
