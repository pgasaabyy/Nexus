from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Turma, Aluno, Professor, Comunicado, EventoCalendario

@login_required
def dashboard(request):
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'turmas': Turma.objects.all()[:4],
    }
    return render(request, 'escola/dashboard.html', context)


@login_required
def gestao_alunos(request):
    alunos = Aluno.objects.all()
    context = {
        'alunos': alunos,
        'total_alunos': Aluno.objects.count(),
    }
    return render(request, 'escola/gestao_alunos.html', context)


@login_required
def gestao_professores(request):
    professores = Professor.objects.all()
    context = {
        'professores': professores,
        'total_professores': Professor.objects.count(),
    }
    return render(request, 'escola/gestao_professores.html', context)


@login_required
def gestao_turmas(request):
    turmas = Turma.objects.all()
    context = {
        'turmas': turmas,
        'total_turmas': Turma.objects.count(),
    }
    return render(request, 'escola/gestao_turmas.html', context)


@login_required
def relatorios(request):
    context = {
        'taxa_aprovacao': 92,
        'taxa_evasao': 1.8,
        'media_geral': 8.4,
        'frequencia_media': 93.5,
    }
    return render(request, 'escola/relatorios.html', context)


@login_required
def calendario(request):
    eventos = EventoCalendario.objects.all()
    context = {
        'eventos': eventos,
    }
    return render(request, 'escola/calendario.html', context)


@login_required
def comunicados(request):
    comunicados = Comunicado.objects.all()
    context = {
        'comunicados': comunicados,
        'total_enviados': Comunicado.objects.filter(enviado=True).count(),
    }
    return render(request, 'escola/comunicados.html', context)


@login_required
def configuracoes(request):
    context = {
        'nome_instituicao': 'Colégio Paulo de Alcântara',
        'ano_atual': 2025,
    }
    return render(request, 'escola/configuracoes.html', context)
