from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Aluno, Nota, Turma, Professor, Disciplina
from .serializers import AlunoSerializer, NotaSerializer

# --- API (Mantida para gráficos futuros) ---
class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

# --- PÁGINAS GERAIS (Login, Home, Logout) ---
def home(request):
    return render(request, 'escola/index.html')

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            login(request, user)
            # Redirecionamento Inteligente
            if user.groups.filter(name='Secretaria').exists():
                return redirect('dashboard_secretaria')
            elif user.groups.filter(name='Coordenacao').exists(): # Atenção ao nome do grupo no Admin
                return redirect('dashboard_coordenacao')
            elif user.groups.filter(name='Professor').exists():
                return redirect('dashboard_professor')
            elif user.groups.filter(name='Aluno').exists():
                return redirect('dashboard_aluno')
            else:
                return redirect('home')
        else:
            return render(request, 'escola/login.html', {'erro': 'Credenciais inválidas'})
            
    return render(request, 'escola/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# =======================================================
# ÁREA DA SECRETARIA
# =======================================================
@login_required
def dashboard_secretaria(request):
    total_alunos = Aluno.objects.count()
    contexto = {'total_alunos': total_alunos}
    return render(request, 'escola/dashboard_secretaria.html', contexto)

@login_required
def secretaria_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'escola/alunos.html', {'alunos': alunos})

@login_required
def secretaria_professores(request):
    professores = Professor.objects.all()
    return render(request, 'escola/professores.html', {'professores': professores})

@login_required
def secretaria_academico(request):
    return render(request, 'escola/academico.html')

@login_required
def secretaria_documentos(request):
    return render(request, 'escola/documentos.html')

# =======================================================
# ÁREA DA COORDENAÇÃO
# =======================================================
@login_required
def dashboard_coordenacao(request):
    return render(request, 'escola/dashboard_coordenacao.html')

@login_required
def coordenacao_turmas(request):
    return render(request, 'escola/coordenacao_turmas.html')

@login_required
def coordenacao_alunos(request):
    # Reutiliza lógica se necessário, ou cria view específica
    return render(request, 'escola/coordenacao_alunos.html')

@login_required
def coordenacao_professores(request):
    return render(request, 'escola/coordenacao_professores.html')

@login_required
def coordenacao_relatorios(request):
    return render(request, 'escola/coordenacao_relatorios.html')

@login_required
def coordenacao_calendario(request):
    return render(request, 'escola/calendario.html') # Compartilhado ou específico

@login_required
def coordenacao_comunicados(request):
    return render(request, 'escola/comunicados.html') # Compartilhado ou específico

@login_required
def coordenacao_configuracoes(request):
    return render(request, 'escola/configuracoes.html') # Compartilhado ou específico

# =======================================================
# ÁREA DO PROFESSOR
# =======================================================
@login_required
def dashboard_professor(request):
    return render(request, 'escola/dashboard_professor.html')

@login_required
def professor_notas(request):
    return render(request, 'escola/professor_notas.html') # Certifique-se de salvar o HTML com este nome

@login_required
def professor_frequencia(request):
    return render(request, 'escola/professor_frequencia.html') # Certifique-se de salvar o HTML com este nome

@login_required
def professor_materiais(request):
    return render(request, 'escola/professor_materiais.html') # Certifique-se de salvar o HTML com este nome

# As views abaixo reutilizam os HTMLs da coordenação (já que são iguais visualmente)
# Se quiser separar, crie arquivos html novos (ex: professor_calendario.html)
@login_required
def professor_calendario(request):
    return render(request, 'escola/calendario.html') 

@login_required
def professor_comunicados(request):
    return render(request, 'escola/comunicados.html')

@login_required
def professor_configuracoes(request):
    return render(request, 'escola/configuracoes.html')

# =======================================================
# ÁREA DO ALUNO (Placeholder para a escola)
# =======================================================
@login_required
def dashboard_aluno(request):
    # Quando chegar na escola, coloque o HTML correto aqui
    return render(request, 'escola/dashboard_aluno.html')