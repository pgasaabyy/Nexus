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
    Aviso, Frequencia, Matricula, Evento, HorarioAula, Curso, Documento, Material
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
    messages.success(request, 'Você saiu do sistema com sucesso.')
    return redirect('home')


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
        return redirect('home')
    
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'atualizar_perfil':
            user.email = request.POST.get('email', user.email)
            user.save()
            
            if aluno:
                aluno.telefone = request.POST.get('telefone', aluno.telefone)
                aluno.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('aluno_configuracoes')
        
        elif action == 'alterar_senha':
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta.')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
            elif len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            else:
                user.set_password(nova_senha)
                user.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
                return redirect('login')
            return redirect('aluno_configuracoes')
    
    context = {
        'aluno': aluno,
        'user': user,
    }
    return render(request, 'escola/aluno_configuracoes.html', context)


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

    eventos = Evento.objects.select_related('turma').order_by('-data')
    eventos_query = Evento.objects.all().values('titulo', 'data', 'tipo', 'turma__codigo')
    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)

    context = {
        'eventos': eventos,
        'eventos_json': eventos_json,
    }
    
    return render(request, 'escola/secre_calendario.html', context)


@login_required
def secretaria_configuracoes(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')
    
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'atualizar_perfil':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('secretaria_configuracoes')
        
        elif action == 'alterar_senha':
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta.')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
            elif len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            else:
                user.set_password(nova_senha)
                user.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
                return redirect('login')
            return redirect('secretaria_configuracoes')
    
    context = {
        'user': user,
    }
    return render(request, 'escola/secre_configuracoes.html', context)


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
    ).order_by('-total_alunos')
    
    turma_id = request.GET.get('turma')
    turma_selecionada = None
    
    if turma_id:
        try:
            turma_selecionada = Turma.objects.annotate(
                total_alunos=Count('alunos_turma')
            ).get(id=turma_id)
        except Turma.DoesNotExist:
            pass
    
    total_alunos = Aluno.objects.count()
    
    context = {
        'turmas': turmas,
        'turma_selecionada': turma_selecionada,
        'total_alunos': total_alunos,
    }
    return render(request, 'escola/coor_relatorios.html', context)


@login_required
def coordenacao_calendario(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    eventos = Evento.objects.select_related('turma').order_by('-data')
    eventos_query = Evento.objects.all().values('titulo', 'data', 'tipo', 'turma__codigo')
    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)
    
    context = {
        'eventos': eventos,
        'eventos_json': eventos_json,
    }
    return render(request, 'escola/coor_calendario.html', context)


@login_required
def coordenacao_comunicados(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    avisos = Aviso.objects.filter(ativo=True).order_by('-data_criacao')
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action', 'adicionar')
        
        if action == 'adicionar':
            titulo = request.POST.get('titulo')
            conteudo = request.POST.get('conteudo')
            turma_id = request.POST.get('turma_id')
            destinatario = request.POST.get('destinatario', 'todos')
            
            if titulo and conteudo:
                aviso = Aviso(
                    titulo=titulo, 
                    conteudo=conteudo,
                    autor=request.user,
                    destinatario=destinatario
                )
                if turma_id:
                    aviso.turma_id = turma_id
                aviso.save()
                messages.success(request, 'Comunicado criado com sucesso!')
            else:
                messages.error(request, 'Preencha título e conteúdo.')
            return redirect('coordenacao_comunicados')
        
        elif action == 'excluir':
            aviso_id = request.POST.get('aviso_id')
            try:
                aviso = Aviso.objects.get(id=aviso_id)
                aviso.ativo = False
                aviso.save()
                messages.success(request, 'Comunicado removido com sucesso!')
            except Aviso.DoesNotExist:
                messages.error(request, 'Comunicado não encontrado.')
            return redirect('coordenacao_comunicados')
        
        elif action == 'editar':
            aviso_id = request.POST.get('aviso_id')
            titulo = request.POST.get('titulo')
            conteudo = request.POST.get('conteudo')
            try:
                aviso = Aviso.objects.get(id=aviso_id)
                aviso.titulo = titulo
                aviso.conteudo = conteudo
                aviso.save()
                messages.success(request, 'Comunicado atualizado com sucesso!')
            except Aviso.DoesNotExist:
                messages.error(request, 'Comunicado não encontrado.')
            return redirect('coordenacao_comunicados')
    
    context = {
        'avisos': avisos,
        'turmas': turmas,
        'destinatarios': Aviso.DESTINATARIO_CHOICES,
    }
    return render(request, 'escola/coor_comunicados.html', context)


@login_required
def coordenacao_configuracoes(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'atualizar_perfil':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('coordenacao_configuracoes')
        
        elif action == 'alterar_senha':
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta.')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
            elif len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            else:
                user.set_password(nova_senha)
                user.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
                return redirect('login')
            return redirect('coordenacao_configuracoes')
    
    context = {
        'user': user,
    }
    return render(request, 'escola/coor_configuracoes.html', context)


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
    total_alunos = sum(t.total_alunos for t in turmas)
    
    context = {
        'professor': professor,
        'turmas': turmas,
        'avisos': avisos,
        'total_alunos': total_alunos
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
    
    professor = getattr(request.user, 'perfil_professor', None)
    disciplinas = Disciplina.objects.all()
    turmas = Turma.objects.all()
    
    materiais = Material.objects.filter(ativo=True).order_by('-data_upload')
    if professor:
        materiais = materiais.filter(professor=professor)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'adicionar' and professor:
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao')
            tipo = request.POST.get('tipo')
            disciplina_id = request.POST.get('disciplina_id')
            turma_id = request.POST.get('turma_id')
            arquivo = request.FILES.get('arquivo')
            
            if titulo and disciplina_id and arquivo:
                material = Material(
                    titulo=titulo,
                    descricao=descricao,
                    tipo=tipo,
                    disciplina_id=disciplina_id,
                    professor=professor,
                    arquivo=arquivo
                )
                if turma_id:
                    material.turma_id = turma_id
                material.save()
                messages.success(request, f'Material "{titulo}" adicionado com sucesso!')
            else:
                messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('professor_materiais')
        
        elif action == 'excluir':
            material_id = request.POST.get('material_id')
            try:
                material = Material.objects.get(id=material_id, professor=professor)
                material.ativo = False
                material.save()
                messages.success(request, 'Material removido com sucesso!')
            except Material.DoesNotExist:
                messages.error(request, 'Material não encontrado.')
            return redirect('professor_materiais')
    
    context = {
        'professor': professor,
        'materiais': materiais,
        'disciplinas': disciplinas,
        'turmas': turmas,
        'tipos': Material.TIPO_CHOICES,
    }
    return render(request, 'escola/professor_materiais.html', context)


@login_required
def professor_calendario(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    professor = getattr(request.user, 'perfil_professor', None)
    turmas = Turma.objects.all()
    eventos = Evento.objects.all().order_by('-data')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'adicionar':
            titulo = request.POST.get('titulo')
            data = request.POST.get('data')
            tipo = request.POST.get('tipo')
            descricao = request.POST.get('descricao')
            turma_id = request.POST.get('turma_id')
            
            if titulo and data and tipo:
                evento = Evento(
                    titulo=titulo,
                    data=data,
                    tipo=tipo,
                    descricao=descricao
                )
                if turma_id:
                    evento.turma_id = turma_id
                evento.save()
                messages.success(request, f'Evento "{titulo}" criado com sucesso!')
            else:
                messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('professor_calendario')
        
        elif action == 'excluir':
            evento_id = request.POST.get('evento_id')
            try:
                evento = Evento.objects.get(id=evento_id)
                evento.delete()
                messages.success(request, 'Evento removido com sucesso!')
            except Evento.DoesNotExist:
                messages.error(request, 'Evento não encontrado.')
            return redirect('professor_calendario')
    
    eventos_query = Evento.objects.all().values('id', 'titulo', 'data', 'tipo', 'turma__codigo', 'descricao')
    eventos_json = json.dumps(list(eventos_query), cls=DjangoJSONEncoder)
    
    context = {
        'professor': professor,
        'eventos': eventos,
        'eventos_json': eventos_json,
        'turmas': turmas,
        'tipos': Evento.TIPO_CHOICES,
    }
    return render(request, 'escola/professor_calendario.html', context)


@login_required
def professor_comunicados(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    professor = getattr(request.user, 'perfil_professor', None)
    turmas = Turma.objects.all()
    
    avisos = Aviso.objects.filter(ativo=True).order_by('-data_criacao')
    meus_avisos = Aviso.objects.filter(autor=request.user, ativo=True).order_by('-data_criacao')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'adicionar':
            titulo = request.POST.get('titulo')
            conteudo = request.POST.get('conteudo')
            turma_id = request.POST.get('turma_id')
            
            if titulo and conteudo:
                aviso = Aviso(
                    titulo=titulo,
                    conteudo=conteudo,
                    autor=request.user,
                    destinatario='turma' if turma_id else 'alunos'
                )
                if turma_id:
                    aviso.turma_id = turma_id
                aviso.save()
                messages.success(request, 'Comunicado enviado com sucesso!')
            else:
                messages.error(request, 'Preencha título e conteúdo.')
            return redirect('professor_comunicados')
        
        elif action == 'excluir':
            aviso_id = request.POST.get('aviso_id')
            try:
                aviso = Aviso.objects.get(id=aviso_id, autor=request.user)
                aviso.ativo = False
                aviso.save()
                messages.success(request, 'Comunicado removido com sucesso!')
            except Aviso.DoesNotExist:
                messages.error(request, 'Comunicado não encontrado ou sem permissão.')
            return redirect('professor_comunicados')
    
    context = {
        'professor': professor,
        'avisos': avisos,
        'meus_avisos': meus_avisos,
        'turmas': turmas,
    }
    return render(request, 'escola/professor_comunicados.html', context)


@login_required
def professor_configuracoes(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    professor = getattr(request.user, 'perfil_professor', None)
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'atualizar_perfil':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            if professor:
                professor.telefone = request.POST.get('telefone', professor.telefone)
                professor.especialidade = request.POST.get('especialidade', professor.especialidade)
                professor.save()
            
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('professor_configuracoes')
        
        elif action == 'alterar_senha':
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta.')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
            elif len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            else:
                user.set_password(nova_senha)
                user.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
                return redirect('login')
            return redirect('professor_configuracoes')
    
    context = {
        'professor': professor,
        'user': user,
    }
    return render(request, 'escola/professor_configuracoes.html', context)


@login_required
def secretaria_aluno_adicionar(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        matricula = request.POST.get('matricula')
        data_nascimento = request.POST.get('data_nascimento')
        telefone = request.POST.get('telefone')
        turma_id = request.POST.get('turma_id')
        
        if nome and email and cpf and matricula and data_nascimento:
            try:
                aluno = Aluno(
                    nome=nome,
                    email=email,
                    cpf=cpf,
                    matricula=matricula,
                    data_nascimento=data_nascimento,
                    telefone=telefone
                )
                if turma_id:
                    aluno.turma_atual_id = turma_id
                aluno.save()
                
                if turma_id:
                    Matricula.objects.create(
                        aluno=aluno,
                        turma_id=turma_id,
                        status='Ativo'
                    )
                
                messages.success(request, f'Aluno {nome} cadastrado com sucesso!')
                return redirect('secretaria_alunos')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar aluno: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/secre_aluno_form.html', {'turmas': turmas, 'acao': 'Adicionar'})


@login_required
def secretaria_aluno_editar(request, aluno_id):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    aluno = get_object_or_404(Aluno, id=aluno_id)
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        aluno.nome = request.POST.get('nome')
        aluno.email = request.POST.get('email')
        aluno.cpf = request.POST.get('cpf')
        aluno.matricula = request.POST.get('matricula')
        aluno.data_nascimento = request.POST.get('data_nascimento')
        aluno.telefone = request.POST.get('telefone')
        turma_id = request.POST.get('turma_id')
        
        if turma_id:
            aluno.turma_atual_id = turma_id
        else:
            aluno.turma_atual = None
        
        try:
            aluno.save()
            messages.success(request, f'Aluno {aluno.nome} atualizado com sucesso!')
            return redirect('secretaria_alunos')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar aluno: {str(e)}')
    
    return render(request, 'escola/secre_aluno_form.html', {
        'turmas': turmas, 
        'aluno': aluno, 
        'acao': 'Editar'
    })


@login_required
def secretaria_aluno_excluir(request, aluno_id):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    if request.method == 'POST':
        nome = aluno.nome
        aluno.delete()
        messages.success(request, f'Aluno {nome} excluído com sucesso!')
        return redirect('secretaria_alunos')
    
    return render(request, 'escola/secre_aluno_excluir.html', {'aluno': aluno})


@login_required
def coordenacao_evento_adicionar(request):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        data = request.POST.get('data')
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao')
        turma_id = request.POST.get('turma_id')
        
        if titulo and data and tipo:
            evento = Evento(
                titulo=titulo,
                data=data,
                tipo=tipo,
                descricao=descricao
            )
            if turma_id:
                evento.turma_id = turma_id
            evento.save()
            messages.success(request, f'Evento "{titulo}" criado com sucesso!')
            return redirect('coordenacao_calendario')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/coor_evento_form.html', {
        'turmas': turmas,
        'tipos': Evento.TIPO_CHOICES,
        'acao': 'Adicionar'
    })


@login_required
def coordenacao_evento_editar(request, evento_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    evento = get_object_or_404(Evento, id=evento_id)
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        evento.titulo = request.POST.get('titulo')
        evento.data = request.POST.get('data')
        evento.tipo = request.POST.get('tipo')
        evento.descricao = request.POST.get('descricao')
        turma_id = request.POST.get('turma_id')
        
        if turma_id:
            evento.turma_id = turma_id
        else:
            evento.turma = None
        
        evento.save()
        messages.success(request, f'Evento "{evento.titulo}" atualizado com sucesso!')
        return redirect('coordenacao_calendario')
    
    return render(request, 'escola/coor_evento_form.html', {
        'turmas': turmas,
        'evento': evento,
        'tipos': Evento.TIPO_CHOICES,
        'acao': 'Editar'
    })


@login_required
def coordenacao_evento_excluir(request, evento_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        titulo = evento.titulo
        evento.delete()
        messages.success(request, f'Evento "{titulo}" excluído com sucesso!')
        return redirect('coordenacao_calendario')
    
    return render(request, 'escola/coor_evento_excluir.html', {'evento': evento})


@login_required
def download_material(request, material_id):
    material = get_object_or_404(Material, id=material_id, ativo=True)
    
    user = request.user
    is_professor = check_professor_permission(user)
    is_secretaria = check_secretaria_permission(user)
    is_coordenacao = check_coordenacao_permission(user)
    
    is_professor_owner = False
    if is_professor and hasattr(user, 'perfil_professor'):
        is_professor_owner = material.professor == user.perfil_professor
    
    is_aluno_turma = False
    if hasattr(user, 'perfil_aluno') and material.turma:
        is_aluno_turma = user.perfil_aluno.turma_atual == material.turma
    
    if not (is_professor_owner or is_secretaria or is_coordenacao or is_aluno_turma or user.is_superuser):
        messages.error(request, 'Você não tem permissão para acessar este material.')
        return redirect('home')
    
    if material.arquivo:
        response = HttpResponse(material.arquivo, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{material.arquivo.name.split("/")[-1]}"'
        return response
    
    messages.error(request, 'Arquivo não encontrado.')
    return redirect('professor_materiais')


@login_required
def coordenacao_turma_adicionar(request):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    cursos = Curso.objects.all()
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        curso_id = request.POST.get('curso_id')
        semestre = request.POST.get('semestre')
        turno = request.POST.get('turno')
        
        if codigo and curso_id:
            try:
                turma = Turma(
                    codigo=codigo,
                    curso_id=curso_id,
                    semestre=semestre,
                    turno=turno
                )
                turma.save()
                messages.success(request, f'Turma {codigo} criada com sucesso!')
                return redirect('coordenacao_turmas')
            except Exception as e:
                messages.error(request, f'Erro ao criar turma: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/coor_turma_form.html', {
        'cursos': cursos,
        'turnos': ['Manhã', 'Tarde', 'Noite', 'Integral'],
        'acao': 'Adicionar'
    })


@login_required
def coordenacao_turma_editar(request, turma_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    turma = get_object_or_404(Turma, id=turma_id)
    cursos = Curso.objects.all()
    
    if request.method == 'POST':
        turma.codigo = request.POST.get('codigo')
        turma.curso_id = request.POST.get('curso_id')
        turma.semestre = request.POST.get('semestre')
        turma.turno = request.POST.get('turno')
        
        try:
            turma.save()
            messages.success(request, f'Turma {turma.codigo} atualizada com sucesso!')
            return redirect('coordenacao_turmas')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar turma: {str(e)}')
    
    return render(request, 'escola/coor_turma_form.html', {
        'turma': turma,
        'cursos': cursos,
        'turnos': ['Manhã', 'Tarde', 'Noite', 'Integral'],
        'acao': 'Editar'
    })


@login_required
def coordenacao_turma_excluir(request, turma_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    turma = get_object_or_404(Turma, id=turma_id)
    
    if request.method == 'POST':
        codigo = turma.codigo
        turma.delete()
        messages.success(request, f'Turma {codigo} excluída com sucesso!')
        return redirect('coordenacao_turmas')
    
    return render(request, 'escola/coor_turma_excluir.html', {'turma': turma})


@login_required
def coordenacao_aluno_adicionar(request):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        matricula = request.POST.get('matricula')
        data_nascimento_str = request.POST.get('data_nascimento')
        telefone = request.POST.get('telefone')
        turma_id = request.POST.get('turma_id')
        
        if nome and email and cpf and matricula and data_nascimento_str:
            try:
                from datetime import datetime
                data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                aluno = Aluno(
                    nome=nome,
                    email=email,
                    cpf=cpf,
                    matricula=matricula,
                    data_nascimento=data_nascimento,
                    telefone=telefone
                )
                if turma_id:
                    aluno.turma_atual_id = turma_id
                aluno.save()
                
                if turma_id:
                    Matricula.objects.create(
                        aluno=aluno,
                        turma_id=turma_id,
                        status='Ativo'
                    )
                
                messages.success(request, f'Aluno {nome} cadastrado com sucesso!')
                return redirect('coordenacao_alunos')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar aluno: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/coor_aluno_form.html', {'turmas': turmas, 'acao': 'Adicionar'})


@login_required
def coordenacao_aluno_editar(request, aluno_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    aluno = get_object_or_404(Aluno, id=aluno_id)
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        aluno.nome = request.POST.get('nome')
        aluno.email = request.POST.get('email')
        aluno.cpf = request.POST.get('cpf')
        aluno.matricula = request.POST.get('matricula')
        data_nascimento_str = request.POST.get('data_nascimento')
        aluno.telefone = request.POST.get('telefone')
        turma_id = request.POST.get('turma_id')
        
        if data_nascimento_str:
            from datetime import datetime
            aluno.data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
        
        if turma_id:
            aluno.turma_atual_id = turma_id
        else:
            aluno.turma_atual = None
        
        try:
            aluno.save()
            messages.success(request, f'Aluno {aluno.nome} atualizado com sucesso!')
            return redirect('coordenacao_alunos')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar aluno: {str(e)}')
    
    return render(request, 'escola/coor_aluno_form.html', {
        'turmas': turmas, 
        'aluno': aluno, 
        'acao': 'Editar'
    })


@login_required
def coordenacao_aluno_excluir(request, aluno_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    if request.method == 'POST':
        nome = aluno.nome
        aluno.delete()
        messages.success(request, f'Aluno {nome} excluído com sucesso!')
        return redirect('coordenacao_alunos')
    
    return render(request, 'escola/coor_aluno_excluir.html', {'aluno': aluno})


@login_required
def coordenacao_professor_adicionar(request):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        especialidade = request.POST.get('especialidade')
        data_admissao_str = request.POST.get('data_admissao')
        criar_usuario = request.POST.get('criar_usuario', 'nao')
        
        if nome and email and data_admissao_str:
            try:
                from datetime import datetime
                data_admissao = datetime.strptime(data_admissao_str, '%Y-%m-%d').date()
                
                professor = Professor(
                    nome=nome,
                    email=email,
                    telefone=telefone,
                    especialidade=especialidade,
                    data_admissao=data_admissao
                )
                
                if criar_usuario == 'sim':
                    from django.contrib.auth.models import User, Group
                    username = email.split('@')[0]
                    if User.objects.filter(username=username).exists():
                        username = f"{username}_{Professor.objects.count() + 1}"
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='senha123',
                        first_name=nome.split()[0] if nome else '',
                        last_name=' '.join(nome.split()[1:]) if len(nome.split()) > 1 else ''
                    )
                    professor_group, _ = Group.objects.get_or_create(name='Professor')
                    user.groups.add(professor_group)
                    professor.usuario = user
                
                professor.save()
                messages.success(request, f'Professor {nome} cadastrado com sucesso!')
                return redirect('coordenacao_professores')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar professor: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return redirect('coordenacao_professores')


@login_required
def coordenacao_professor_editar(request, professor_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    professor = get_object_or_404(Professor, id=professor_id)
    
    if request.method == 'POST':
        professor.nome = request.POST.get('nome')
        professor.email = request.POST.get('email')
        professor.telefone = request.POST.get('telefone')
        professor.especialidade = request.POST.get('especialidade')
        data_admissao_str = request.POST.get('data_admissao')
        
        if data_admissao_str:
            from datetime import datetime
            professor.data_admissao = datetime.strptime(data_admissao_str, '%Y-%m-%d').date()
        
        try:
            professor.save()
            messages.success(request, f'Professor {professor.nome} atualizado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar professor: {str(e)}')
    
    return redirect('coordenacao_professores')


@login_required
def coordenacao_professor_excluir(request, professor_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    professor = get_object_or_404(Professor, id=professor_id)
    
    if request.method == 'POST':
        nome = professor.nome
        professor.delete()
        messages.success(request, f'Professor {nome} excluído com sucesso!')
    
    return redirect('coordenacao_professores')
