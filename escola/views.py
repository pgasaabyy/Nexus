from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Aluno, Nota, Turma
from .serializers import AlunoSerializer, NotaSerializer

# --- PARTE 1: API (Para os gráficos) ---
class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

# --- PARTE 2: PÁGINAS DO SITE (HTML) ---

def home(request):
    return render(request, 'escola/index.html')

def login_view(request):
    if request.method == 'POST':
        # Pega dados do HTML
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            login(request, user)
            # Redirecionamento Inteligente por Grupo
            if user.groups.filter(name='Secretaria').exists():
                return redirect('dashboard_secretaria')
            elif user.groups.filter(name='Professor').exists():
                return redirect('dashboard_professor')
            elif user.groups.filter(name='Aluno').exists():
                return redirect('dashboard_aluno')
            else:
                return redirect('home') # Se não tiver grupo, vai pra home
        else:
            # Se errou a senha, volta pro login com erro (opcional tratar no HTML)
            return render(request, 'escola/login.html', {'erro': 'Credenciais inválidas'})
            
    return render(request, 'escola/login.html')

@login_required
def dashboard_secretaria(request):
    # Exemplo de dados para o dashboard
    total_alunos = Aluno.objects.count()
    contexto = {'total_alunos': total_alunos}
    return render(request, 'escola/dashboard_secretaria.html', contexto)

@login_required
def dashboard_professor(request):
    return render(request, 'escola/dashboard_prof.html')

@login_required
def dashboard_aluno(request):
    return render(request, 'escola/dashboard_aluno.html')