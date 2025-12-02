import json
import io
from decimal import Decimal
from django.db.models import Q, Count, Avg
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from openpyxl import Workbook
from django.utils import timezone

from .models import (
    Aluno, Nota, Turma, Professor, Disciplina, 
    Aviso, Frequencia, Matricula, Evento, HorarioAula, Curso, Documento
)
from .serializers import AlunoSerializer, NotaSerializer


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer


class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer


def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)
    
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            login(request, user)
            return redirect_user_by_role(user)
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'escola/login.html')


def redirect_user_by_role(user):
    """Redireciona o usuário para o dashboard apropriado baseado em sua função."""
    if user.is_superuser:
        return redirect('/admin/')
    
    # Verifica se é aluno (via OneToOne relationship)
    try:
        if hasattr(user, 'perfil_aluno') and user.perfil_aluno:
            return redirect('dashboard_aluno')
    except Aluno.DoesNotExist:
        pass
    
    # Verifica se é professor (via OneToOne relationship)
    try:
        if hasattr(user, 'perfil_professor') and user.perfil_professor:
            return redirect('dashboard_professor')
    except Professor.DoesNotExist:
        pass
    
    # Fallback: tenta encontrar por email
    if Aluno.objects.filter(email=user.email).exists():
        aluno = Aluno.objects.get(email=user.email)
        if not aluno.user:
            aluno.user = user
            aluno.save()
        return redirect('dashboard_aluno')
    
    if Professor.objects.filter(email=user.email).exists():
        professor = Professor.objects.get(email=user.email)
        if not professor.user:
            professor.user = user
            professor.save()
        return redirect('dashboard_professor')
    
    # Verifica grupos de permissão
    user_groups = user.groups.values_list('name', flat=True)
    
    if 'secretaria' in [g.lower() for g in user_groups]:
        return redirect('dashboard_secretaria')
    
    if 'coordenacao' in [g.lower() for g in user_groups]:
        return redirect('dashboard_coordenacao')
    
    # Fallback para home
    return redirect('home')


def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, 'escola/index.html')


@login_required
def dashboard_aluno(request):
    try:
        aluno = request.user.perfil_aluno
        media_geral = aluno.calcular_media_geral()
        faltas_totais = aluno.contar_faltas()
    except AttributeError:
        messages.error(request, 'Perfil de aluno não encontrado.')
        return redirect('home')

    avisos = Aviso.objects.order_by('-data_criacao')[:5]

    context = {
        'aluno': aluno,
        'media': media_geral,
        'faltas': faltas_totais,
        'avisos': avisos
    }
    return render(request, 'escola/aluno_dashboard.html', context)


@login_required
def aluno_boletim(request):
    try:
        aluno = request.user.perfil_aluno
        turma = aluno.turma_atual
    except AttributeError:
        return redirect('home')

    boletim_completo = []
    if turma:
        disciplinas = turma.curso.disciplinas.all()
        for disciplina in disciplinas:
            notas = Nota.objects.filter(matricula__aluno=aluno, disciplina=disciplina)
            lista_notas = [float(n.valor) for n in notas]
            media = sum(lista_notas) / len(lista_notas) if lista_notas else 0
            
            status = "Aprovado" if media >= 6 else "Recuperação"
            if not lista_notas:
                status = "Cursando"

            boletim_completo.append({
                'disciplina': disciplina.nome,
                'notas': lista_notas,
                'media': round(media, 1),
                'status': status
            })

    contexto = {
        'aluno': aluno,
        'boletim': boletim_completo
    }
    return render(request, 'escola/aluno_boletim.html', contexto)


@login_required
def aluno_frequencia(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    frequencia_detalhada = []
    total_presenca = 0
    total_aulas_geral = 0
    
    if aluno.turma_atual:
        for disciplina in aluno.turma_atual.curso.disciplinas.all():
            faltas = Frequencia.objects.filter(
                matricula__aluno=aluno, 
                disciplina=disciplina, 
                presente=False
            ).count()
            
            total_aulas = Frequencia.objects.filter(
                matricula__aluno=aluno, 
                disciplina=disciplina
            ).count()

            porcentagem = 100
            if total_aulas > 0:
                presencas = total_aulas - faltas
                porcentagem = int((presencas / total_aulas) * 100)
                total_presenca += presencas
                total_aulas_geral += total_aulas

            status = "Regular"
            if porcentagem < 75:
                status = "Atenção"
            if porcentagem == 100:
                status = "Excelente"

            frequencia_detalhada.append({
                'disciplina': disciplina.nome,
                'faltas': faltas,
                'total_aulas': total_aulas,
                'porcentagem': porcentagem,
                'status': status
            })

    porcentagem_geral = int((total_presenca / total_aulas_geral) * 100) if total_aulas_geral > 0 else 100
    
    contexto = {
        'aluno': aluno,
        'frequencia': frequencia_detalhada,
        'porcentagem_geral': porcentagem_geral
    }
    return render(request, 'escola/aluno_frequencia.html', contexto)


@login_required
def aluno_horario(request):
    try:
        aluno = request.user.perfil_aluno
        turma = aluno.turma_atual
    except AttributeError:
        return redirect('home')

    grade_horaria = {}
    horarios_padrao = ["07:00", "07:50", "08:40", "09:30", "09:50", "10:40", "11:30"]

    if turma:
        aulas = HorarioAula.objects.filter(turma=turma).select_related('disciplina')
        
        for hora in horarios_padrao:
            grade_horaria[hora] = {'SEG': None, 'TER': None, 'QUA': None, 'QUI': None, 'SEX': None}
            
            for aula in aulas:
                if aula.hora_inicio.strftime('%H:%M') == hora:
                    grade_horaria[hora][aula.dia_semana] = aula.disciplina.nome

    return render(request, 'escola/aluno_horario.html', {
        'aluno': aluno, 
        'grade': grade_horaria
    })


@login_required
def aluno_calendario(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    eventos_query = Evento.objects.filter(
        Q(turma__isnull=True) | Q(turma=aluno.turma_atual)
    ).values('titulo', 'data', 'tipo')

    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)

    return render(request, 'escola/aluno_calendario.html', {
        'aluno': aluno,
        'eventos_json': eventos_json
    })


@login_required
def aluno_justificativa(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        aluno = None
    return render(request, 'escola/aluno_justificativa.html', {'aluno': aluno})


@login_required
def aluno_evento(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        aluno = None
    return render(request, 'escola/aluno_evento.html', {'aluno': aluno})


@login_required
def aluno_configuracoes(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        aluno = None
    return render(request, 'escola/aluno_configuracoes.html', {'aluno': aluno})


@login_required
def exportar_boletim_pdf(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "Boletim Escolar - Nexus")
    p.setFont("Helvetica", 12)
    p.drawString(50, 780, f"Aluno: {aluno.nome}")
    p.drawString(50, 765, f"Matrícula: {aluno.matricula}")
    p.drawString(50, 750, f"Turma: {aluno.turma_atual.codigo if aluno.turma_atual else 'Sem Turma'}")
    
    p.line(50, 740, 550, 740)
    
    y = 710
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "DISCIPLINA")
    p.drawString(250, y, "MÉDIA")
    p.drawString(400, y, "SITUAÇÃO")
    y -= 20

    if aluno.turma_atual:
        for disciplina in aluno.turma_atual.curso.disciplinas.all():
            notas = Nota.objects.filter(matricula__aluno=aluno, disciplina=disciplina)
            lista_notas = [float(n.valor) for n in notas]
            media = sum(lista_notas) / len(lista_notas) if lista_notas else 0
            status = "Aprovado" if media >= 6 else "Recuperação"
            if not lista_notas:
                status = "Cursando"

            p.setFont("Helvetica", 10)
            p.drawString(50, y, str(disciplina.nome))
            p.drawString(250, y, str(round(media, 1)))
            
            if status == "Recuperação":
                p.setFillColor(colors.red)
            elif status == "Aprovado":
                p.setFillColor(colors.green)
            else:
                p.setFillColor(colors.black)
                
            p.drawString(400, y, status)
            p.setFillColor(colors.black)
            y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.matricula}.pdf"'
    return response


@login_required
def exportar_frequencia_pdf(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "Relatório de Frequência - Nexus")
    p.setFont("Helvetica", 12)
    p.drawString(50, 780, f"Aluno: {aluno.nome}")
    
    y = 740
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "DISCIPLINA")
    p.drawString(250, y, "FALTAS")
    p.drawString(350, y, "% PRESENÇA")
    y -= 20

    if aluno.turma_atual:
        for disciplina in aluno.turma_atual.curso.disciplinas.all():
            faltas = Frequencia.objects.filter(matricula__aluno=aluno, disciplina=disciplina, presente=False).count()
            total = Frequencia.objects.filter(matricula__aluno=aluno, disciplina=disciplina).count()
            porc = int(((total - faltas) / total) * 100) if total > 0 else 100

            p.setFont("Helvetica", 10)
            p.drawString(50, y, str(disciplina.nome))
            p.drawString(250, y, str(faltas))
            p.drawString(350, y, f"{porc}%")
            y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="frequencia_{aluno.matricula}.pdf"'
    return response


@login_required
def exportar_frequencia_excel(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    wb = Workbook()
    ws = wb.active
    ws.title = "Frequência"
    ws.append(['Disciplina', 'Total Aulas', 'Faltas', '% Presença', 'Situação'])

    if aluno.turma_atual:
        for disciplina in aluno.turma_atual.curso.disciplinas.all():
            faltas = Frequencia.objects.filter(matricula__aluno=aluno, disciplina=disciplina, presente=False).count()
            total = Frequencia.objects.filter(matricula__aluno=aluno, disciplina=disciplina).count()
            porc = int(((total - faltas) / total) * 100) if total > 0 else 100
            status = "Atenção" if porc < 75 else "Regular"
            ws.append([disciplina.nome, total, faltas, f"{porc}%", status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=frequencia_{aluno.matricula}.xlsx'
    wb.save(response)
    return response


def check_secretaria_permission(user):
    return user.is_superuser or user.groups.filter(name__iexact='secretaria').exists()


def check_coordenacao_permission(user):
    return user.is_superuser or user.groups.filter(name__iexact='coordenacao').exists()


def check_professor_permission(user):
    return user.is_superuser or hasattr(user, 'perfil_professor')


@login_required
def dashboard_secretaria(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')

    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    total_cursos = Curso.objects.count()
    
    ultimos_alunos = Aluno.objects.order_by('-id')[:5]
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()

    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'total_cursos': total_cursos,
        'ultimos_alunos': ultimos_alunos,
        'documentos_pendentes': documentos_pendentes
    }
    
    return render(request, 'escola/secre_dashboard.html', context)


@login_required
def secretaria_alunos(request):
    if not check_secretaria_permission(request.user):
        return redirect('home')
    
    alunos = Aluno.objects.all().order_by('nome')
    turmas = Turma.objects.all()
    
    busca = request.GET.get('busca', '')
    turma_filtro = request.GET.get('turma', '')
    
    if busca:
        alunos = alunos.filter(Q(nome__icontains=busca) | Q(matricula__icontains=busca))
    if turma_filtro:
        alunos = alunos.filter(turma_atual_id=turma_filtro)
    
    return render(request, 'escola/secre_alunos.html', {
        'alunos': alunos,
        'turmas': turmas,
        'busca': busca,
        'turma_filtro': turma_filtro
    })


@login_required
def secretaria_professores(request):
    if not check_secretaria_permission(request.user):
        return redirect('home')
    
    professores = Professor.objects.all().order_by('nome')
    return render(request, 'escola/secre_professores.html', {'professores': professores})


@login_required
def secretaria_academico(request):
    if not check_secretaria_permission(request.user):
        return redirect('home')
    
    cursos = Curso.objects.annotate(total_turmas=Count('turma'))
    turmas = Turma.objects.annotate(total_alunos=Count('alunos_turma'))
    disciplinas = Disciplina.objects.all()
    
    context = {
        'cursos': cursos,
        'turmas': turmas,
        'disciplinas': disciplinas
    }
    return render(request, 'escola/secre_academico.html', context)


@login_required
def secretaria_documentos(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')

    tipo_filtro = request.GET.get('tipo')
    status_filtro = request.GET.get('status')
    busca_aluno = request.GET.get('aluno')

    documentos = Documento.objects.select_related('aluno').order_by('-data_solicitacao')

    if tipo_filtro and tipo_filtro != 'TODOS':
        documentos = documentos.filter(tipo=tipo_filtro)

    if status_filtro and status_filtro != 'TODOS':
        documentos = documentos.filter(status=status_filtro)

    if busca_aluno:
        documentos = documentos.filter(aluno__nome__icontains=busca_aluno)

    if request.method == 'POST':
        aluno_id = request.POST.get('aluno_id')
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao')

        if not aluno_id or not tipo:
            messages.error(request, "Selecione um aluno e um tipo.")
        else:
            try:
                aluno = Aluno.objects.get(id=aluno_id)
                Documento.objects.create(
                    aluno=aluno,
                    tipo=tipo,
                    descricao=descricao,
                    status='PENDENTE',
                    criado_por=request.user
                )
                messages.success(request, f"Documento criado para o aluno {aluno.nome}.")
                return redirect('secretaria_documentos')
            except Aluno.DoesNotExist:
                messages.error(request, "Aluno não encontrado.")

    context = {
        'documentos': documentos,
        'tipos_choices': Documento.TIPOS_CHOICES,
        'status_choices': Documento.STATUS_CHOICES,
        'tipo_filtro': tipo_filtro or 'TODOS',
        'status_filtro': status_filtro or 'TODOS',
        'busca_aluno': busca_aluno or '',
        'alunos': Aluno.objects.all().order_by('nome'),
    }

    return render(request, 'escola/secre_documentos.html', context)


@login_required
def secretaria_calendario(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')

    eventos_query = Evento.objects.all().values('titulo', 'data', 'tipo', 'turma__codigo')
    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)

    context = {
        'eventos_json': eventos_json,
    }
    
    return render(request, 'escola/secre_calendario.html', context)


@login_required
def secretaria_configuracoes(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')
    return render(request, 'escola/secre_configuracoes.html')


@login_required
def dashboard_coordenacao(request):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    turmas = Turma.objects.annotate(
        total_alunos=Count('alunos_turma')
    ).order_by('-total_alunos')[:5]
    
    avisos_recentes = Aviso.objects.order_by('-data_criacao')[:5]
    
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'turmas': turmas,
        'avisos': avisos_recentes
    }
    return render(request, 'escola/coor_dashboard.html', context)


@login_required
def coordenacao_turmas(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    turmas = Turma.objects.annotate(total_alunos=Count('alunos_turma')).order_by('codigo')
    cursos = Curso.objects.all()
    
    context = {
        'turmas': turmas,
        'cursos': cursos
    }
    return render(request, 'escola/coor_turmas.html', context)


@login_required
def coordenacao_alunos(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    alunos = Aluno.objects.all().order_by('nome')
    turmas = Turma.objects.all()
    
    busca = request.GET.get('busca', '')
    turma_filtro = request.GET.get('turma', '')
    
    if busca:
        alunos = alunos.filter(Q(nome__icontains=busca) | Q(matricula__icontains=busca))
    if turma_filtro:
        alunos = alunos.filter(turma_atual_id=turma_filtro)
    
    context = {
        'alunos': alunos,
        'turmas': turmas,
        'busca': busca,
        'turma_filtro': turma_filtro
    }
    return render(request, 'escola/coor_alunos.html', context)


@login_required
def coordenacao_professores(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    professores = Professor.objects.all().order_by('nome')
    return render(request, 'escola/coor_professores.html', {'professores': professores})


@login_required
def coordenacao_relatorios(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    turmas = Turma.objects.annotate(
        total_alunos=Count('alunos_turma')
    )
    
    context = {
        'turmas': turmas
    }
    return render(request, 'escola/coor_relatorios.html', context)


@login_required
def coordenacao_calendario(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    eventos_query = Evento.objects.all().values('titulo', 'data', 'tipo', 'turma__codigo')
    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)
    
    context = {
        'eventos_json': eventos_json,
    }
    return render(request, 'escola/coor_calendario.html', context)


@login_required
def coordenacao_comunicados(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    avisos = Aviso.objects.order_by('-data_criacao')
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')
        turma_id = request.POST.get('turma_id')
        
        if titulo and conteudo:
            aviso = Aviso(titulo=titulo, conteudo=conteudo)
            if turma_id:
                aviso.turma_id = turma_id
            aviso.save()
            messages.success(request, 'Comunicado criado com sucesso!')
            return redirect('coordenacao_comunicados')
    
    context = {
        'avisos': avisos,
        'turmas': turmas
    }
    return render(request, 'escola/coor_comunicados.html', context)


@login_required
def coordenacao_configuracoes(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    return render(request, 'escola/coor_configuracoes.html')


@login_required
def dashboard_professor(request):
    if not check_professor_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    professor = None
    turmas = []
    
    if hasattr(request.user, 'perfil_professor'):
        professor = request.user.perfil_professor
    
    turmas = Turma.objects.annotate(total_alunos=Count('alunos_turma'))[:5]
    avisos = Aviso.objects.order_by('-data_criacao')[:3]
    
    context = {
        'professor': professor,
        'turmas': turmas,
        'avisos': avisos
    }
    return render(request, 'escola/dashboard_professor.html', context)


@login_required
def professor_notas(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.all()
    
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    
    alunos = []
    turma_selecionada = None
    disciplina_selecionada = None
    
    if turma_id:
        turma_selecionada = get_object_or_404(Turma, id=turma_id)
        alunos = Aluno.objects.filter(turma_atual=turma_selecionada).order_by('nome')
        
        if disciplina_id:
            disciplina_selecionada = get_object_or_404(Disciplina, id=disciplina_id)
            
            for aluno in alunos:
                matricula = Matricula.objects.filter(aluno=aluno, turma=turma_selecionada).first()
                if matricula:
                    notas = Nota.objects.filter(matricula=matricula, disciplina=disciplina_selecionada)
                    aluno.notas_disciplina = list(notas)
                    if notas:
                        aluno.media = sum([float(n.valor) for n in notas]) / len(notas)
                    else:
                        aluno.media = 0
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'alunos': alunos,
        'turma_selecionada': turma_selecionada,
        'disciplina_selecionada': disciplina_selecionada
    }
    return render(request, 'escola/professor_notas.html', context)


@login_required
def professor_salvar_notas(request):
    if not check_professor_permission(request.user):
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma_id')
        disciplina_id = request.POST.get('disciplina_id')
        tipo_avaliacao = request.POST.get('tipo_avaliacao', 'Prova')
        
        turma = get_object_or_404(Turma, id=turma_id)
        disciplina = get_object_or_404(Disciplina, id=disciplina_id)
        
        for key, value in request.POST.items():
            if key.startswith('nota_'):
                aluno_id = key.replace('nota_', '')
                try:
                    aluno = Aluno.objects.get(id=aluno_id)
                    matricula = Matricula.objects.filter(aluno=aluno, turma=turma).first()
                    
                    if matricula and value:
                        Nota.objects.create(
                            matricula=matricula,
                            disciplina=disciplina,
                            valor=Decimal(value),
                            tipo_avaliacao=tipo_avaliacao
                        )
                except (Aluno.DoesNotExist, ValueError):
                    continue
        
        messages.success(request, 'Notas salvas com sucesso!')
        return redirect('professor_notas')
    
    return redirect('professor_notas')


@login_required
def professor_frequencia(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.all()
    
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    data = request.GET.get('data', timezone.now().strftime('%Y-%m-%d'))
    
    alunos = []
    turma_selecionada = None
    disciplina_selecionada = None
    
    if turma_id:
        turma_selecionada = get_object_or_404(Turma, id=turma_id)
        alunos = Aluno.objects.filter(turma_atual=turma_selecionada).order_by('nome')
        
        if disciplina_id:
            disciplina_selecionada = get_object_or_404(Disciplina, id=disciplina_id)
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'alunos': alunos,
        'turma_selecionada': turma_selecionada,
        'disciplina_selecionada': disciplina_selecionada,
        'data_aula': data
    }
    return render(request, 'escola/professor_frequencia.html', context)


@login_required
def professor_salvar_frequencia(request):
    if not check_professor_permission(request.user):
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma_id')
        disciplina_id = request.POST.get('disciplina_id')
        data_aula = request.POST.get('data_aula')
        
        turma = get_object_or_404(Turma, id=turma_id)
        disciplina = get_object_or_404(Disciplina, id=disciplina_id)
        
        alunos = Aluno.objects.filter(turma_atual=turma)
        
        for aluno in alunos:
            matricula = Matricula.objects.filter(aluno=aluno, turma=turma).first()
            if matricula:
                presente = request.POST.get(f'presente_{aluno.id}') == 'on'
                
                Frequencia.objects.update_or_create(
                    matricula=matricula,
                    disciplina=disciplina,
                    data_aula=data_aula,
                    defaults={'presente': presente}
                )
        
        messages.success(request, 'Frequência salva com sucesso!')
        return redirect('professor_frequencia')
    
    return redirect('professor_frequencia')


@login_required
def professor_materiais(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    return render(request, 'escola/professor_materiais.html')


@login_required
def professor_calendario(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    eventos_query = Evento.objects.all().values('titulo', 'data', 'tipo', 'turma__codigo')
    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)
    
    context = {
        'eventos_json': eventos_json,
    }
    return render(request, 'escola/professor_calendario.html', context)


@login_required
def professor_comunicados(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    avisos = Aviso.objects.order_by('-data_criacao')
    return render(request, 'escola/professor_comunicados.html', {'avisos': avisos})


@login_required
def professor_configuracoes(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    return render(request, 'escola/professor_configuracoes.html')
