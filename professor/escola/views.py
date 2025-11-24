from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Comunicado, Material, Evento, Nota, Aluno, Turma, Escola
from django.utils import timezone

@login_required
def dashboard_professor(request):
    """Dashboard principal do professor"""
    usuario = request.user
    try:
        escola = Escola.objects.first()
    except:
        escola = None
    
    notas_lancadas = Nota.objects.filter(professor=usuario).count()
    turmas = Turma.objects.filter(professores=usuario)
    total_alunos = Aluno.objects.filter(turma__in=turmas).count()
    aulas_mes = Nota.objects.filter(professor=usuario, data_lancamento__month=timezone.now().month).count()
    
    context = {
        'usuario': usuario,
        'escola': escola,
        'notas_lancadas': notas_lancadas,
        'total_alunos': total_alunos,
        'aulas_mes': aulas_mes,
        'turmas': turmas,
    }
    return render(request, 'dashboard-professor.html', context)

@login_required
def lancamento_notas(request):
    """Página de lançamento de notas"""
    turmas = Turma.objects.filter(professores=request.user)
    turma_id = request.GET.get('turma')
    bimestre = request.GET.get('bimestre', '4')
    
    notas = []
    turma_selecionada = None
    
    if turma_id:
        try:
            turma_selecionada = Turma.objects.get(id=turma_id)
            alunos = turma_selecionada.alunos.all()
            for aluno in alunos:
                nota = Nota.objects.filter(aluno=aluno, bimestre=bimestre).first()
                notas.append({'aluno': aluno, 'nota': nota})
        except Turma.DoesNotExist:
            pass
    
    context = {
        'turmas': turmas,
        'turma_selecionada': turma_selecionada,
        'notas': notas,
        'bimestre': bimestre,
    }
    return render(request, 'lancamento-notas.html', context)

@login_required
def frequencia(request):
    """Página de registro de frequência"""
    turmas = Turma.objects.filter(professores=request.user)
    turma_id = request.GET.get('turma')
    data_aula = request.GET.get('data')
    
    alunos = []
    turma_selecionada = None
    
    if turma_id:
        try:
            turma_selecionada = Turma.objects.get(id=turma_id)
            alunos = turma_selecionada.alunos.all()
        except Turma.DoesNotExist:
            pass
    
    context = {
        'turmas': turmas,
        'turma_selecionada': turma_selecionada,
        'alunos': alunos,
        'data_aula': data_aula,
    }
    return render(request, 'frequencia.html', context)

@login_required
def materiais(request):
    """Página de materiais didáticos"""
    turmas = Turma.objects.filter(professores=request.user)
    materiais = Material.objects.filter(professor=request.user).order_by('-data_envio')
    
    context = {
        'turmas': turmas,
        'materiais': materiais,
    }
    return render(request, 'materiais.html', context)

@login_required
def calendario(request):
    """Página de calendário acadêmico"""
    eventos = Evento.objects.all().order_by('data')
    
    context = {
        'eventos': eventos,
    }
    return render(request, 'calendario.html', context)

@login_required
def comunicados(request):
    """Página de comunicados"""
    comunicados_enviados = Comunicado.objects.filter(professor=request.user).order_by('-data_envio')
    
    context = {
        'comunicados': comunicados_enviados,
    }
    return render(request, 'comunicados.html', context)

@login_required
def configuracoes(request):
    """Página de configurações"""
    try:
        escola = Escola.objects.first()
    except:
        escola = None
    
    context = {
        'escola': escola,
    }
    return render(request, 'configuracoes.html', context)
