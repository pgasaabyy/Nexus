import json
import io
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from openpyxl import Workbook
from django.db.models import Count
from django.utils import timezone
from .models import Documento
from django.shortcuts import render
from django.shortcuts import render
from .models import Evento


# IMPORTAÇÃO DOS MODELOS
from .models import (
    Aluno, Nota, Turma, Professor, Disciplina, 
    Aviso, Frequencia, Matricula, Evento, HorarioAula, Curso
)
from .serializers import AlunoSerializer, NotaSerializer

# --- API (Mantida para uso futuro) ---
class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

# =======================================================
# PÁGINAS GERAIS (LOGIN / HOME)
# =======================================================

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            login(request, user)

            # Superusuário
            if user.is_superuser:
                return redirect('/admin/')

            # Aluno
            if user.groups.filter(name='aluno').exists():
                return redirect('dashboard_aluno')

            # Secretaria
            if user.groups.filter(name='secretaria').exists():
                return redirect('dashboard_secretaria')

            # Professor
            if user.groups.filter(name='professor').exists():
                return redirect('dashboard_professor')

            # Coordenador
            if user.groups.filter(name='coordenacao').exists():
                return redirect('dashboard_coordenacao')

            # fallback
            return redirect('home')

        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'escola/login.html')


    


def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'escola/index.html')


# =======================================================
# ÁREA DO ALUNO (Lógica Completa)
# =======================================================



@login_required
def dashboard_aluno(request):
    try:
        aluno = request.user.perfil_aluno
        media_geral = aluno.calcular_media_geral()
        faltas_totais = aluno.contar_faltas()
    except AttributeError:
        return redirect('home')

    avisos = Aviso.objects.order_by('-data_criacao')[:3]

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
            lista_notas = [n.valor for n in notas]
            media = sum(lista_notas) / len(lista_notas) if lista_notas else 0
            
            status = "Aprovado" if media >= 6 else "Recuperação"
            if not lista_notas: status = "Cursando"

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

            status = "Regular"
            if porcentagem < 75: status = "Atenção"
            if porcentagem == 100: status = "Excelente"

            frequencia_detalhada.append({
                'disciplina': disciplina.nome,
                'faltas': faltas,
                'total_aulas': total_aulas,
                'porcentagem': porcentagem,
                'status': status
            })

    contexto = {
        'aluno': aluno,
        'frequencia': frequencia_detalhada
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

# --- Views Simples ---
@login_required
def aluno_justificativa(request):
    try: aluno = request.user.perfil_aluno
    except AttributeError: aluno = None
    return render(request, 'escola/aluno_justificativa.html', {'aluno': aluno})

@login_required
def aluno_evento(request):
    try: aluno = request.user.perfil_aluno
    except AttributeError: aluno = None
    return render(request, 'escola/aluno_evento.html', {'aluno': aluno})

@login_required
def aluno_configuracoes(request):
    try: aluno = request.user.perfil_aluno
    except AttributeError: aluno = None
    return render(request, 'escola/aluno_configuracoes.html', {'aluno': aluno})

# =======================================================
# FUNÇÕES DE EXPORTAÇÃO (PDF/EXCEL)
# =======================================================

@login_required
def exportar_boletim_pdf(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.matricula}.pdf"'
    
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
            lista_notas = [n.valor for n in notas]
            media = sum(lista_notas) / len(lista_notas) if lista_notas else 0
            status = "Aprovado" if media >= 6 else "Recuperação"
            if not lista_notas: status = "Cursando"

            p.setFont("Helvetica", 10)
            p.drawString(50, y, str(disciplina.nome))
            p.drawString(250, y, str(round(media, 1)))
            
            if status == "Recuperação": p.setFillColor(colors.red)
            elif status == "Aprovado": p.setFillColor(colors.green)
            else: p.setFillColor(colors.black)
                
            p.drawString(400, y, status)
            p.setFillColor(colors.black)
            y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def exportar_frequencia_pdf(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        return redirect('home')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="frequencia_{aluno.matricula}.pdf"'
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, f"Relatório de Frequência - Nexus")
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
            porc = int(((total - faltas)/total)*100) if total > 0 else 100

            p.setFont("Helvetica", 10)
            p.drawString(50, y, str(disciplina.nome))
            p.drawString(250, y, str(faltas))
            p.drawString(350, y, f"{porc}%")
            y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

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
            porc = int(((total - faltas)/total)*100) if total > 0 else 100
            status = "Atenção" if porc < 75 else "Regular"
            ws.append([disciplina.nome, total, faltas, f"{porc}%", status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=frequencia_{aluno.matricula}.xlsx'
    wb.save(response)
    return response

# =======================================================
# ÁREA DA SECRETARIA (Gestão Completa)
# =======================================================

@login_required
def dashboard_secretaria(request):
    # Segurança: Verifica grupo OU Superusuário (mas sem redirecionar admin pro admin)
    if not request.user.is_superuser and not request.user.groups.filter(name='Secretaria').exists():
        return redirect('home')

    # KPIs
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    # Lista Recente
    ultimos_alunos = Aluno.objects.order_by('-id')[:5]

    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'ultimos_alunos': ultimos_alunos
    }
    
    return render(request, 'escola/secre_dashboard.html', context)

@login_required
def secretaria_alunos(request):
    alunos = Aluno.objects.all().order_by('nome')
    return render(request, 'escola/secre_alunos.html', {'alunos': alunos})

@login_required
def secretaria_professores(request):
    professores = Professor.objects.all().order_by('nome')
    return render(request, 'escola/secre_professores.html', {'professores': professores})

@login_required
def secretaria_academico(request):
    # Otimização com Count para evitar muitas queries
    from django.db.models import Count
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
    # Validação de acesso igual às outras páginas da secretaria
    if not request.user.is_superuser and not request.user.groups.filter(name='Secretaria').exists():
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')
        from django.utils import timezone
from .models import Documento  # importa o model novo

@login_required
@login_required
def secretaria_documentos(request):
    # 1. Segurança: só Secretaria ou Superusuário
    if not request.user.is_superuser and not request.user.groups.filter(name='Secretaria').exists():
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')

    # 2. Filtros (GET)
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

    # 3. Cadastro (POST)
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
    if not request.user.is_superuser and not request.user.groups.filter(name='Secretaria').exists():
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
    if not request.user.is_superuser and not request.user.groups.filter(name='Secretaria').exists():
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')
    return render(request, 'escola/secre_configuracoes.html')
    return render(request, 'escola/secre_documentos.html')

# =======================================================
# ÁREA DA COORDENAÇÃO (Placeholders)
# =======================================================
@login_required
def dashboard_coordenacao(request):
    return render(request, 'escola/dashboard_coordenacao.html')

@login_required
def coordenacao_turmas(request):
    return render(request, 'escola/coordenacao_turmas.html')

@login_required
def coordenacao_alunos(request):
    return render(request, 'escola/coordenacao_alunos.html')

@login_required
def coordenacao_professores(request):
    return render(request, 'escola/coordenacao_professores.html')

@login_required
def coordenacao_relatorios(request):
    return render(request, 'escola/coordenacao_relatorios.html')

@login_required
def coordenacao_calendario(request):
    return render(request, 'escola/calendario.html')

@login_required
def coordenacao_comunicados(request):
    return render(request, 'escola/comunicados.html')

@login_required
def coordenacao_configuracoes(request):
    return render(request, 'escola/configuracoes.html')

# =======================================================
# ÁREA DO PROFESSOR (Placeholders)
# =======================================================
@login_required
def dashboard_professor(request):
    return render(request, 'escola/dashboard_professor.html')

@login_required
def professor_notas(request):
    return render(request, 'escola/professor_notas.html')

@login_required
def professor_frequencia(request):
    return render(request, 'escola/professor_frequencia.html')

@login_required
def professor_materiais(request):
    return render(request, 'escola/professor_materiais.html')

@login_required
def professor_calendario(request):
    return render(request, 'escola/calendario.html') 

@login_required
def professor_comunicados(request):
    return render(request, 'escola/comunicados.html')

@login_required
def professor_configuracoes(request):
    return render(request, 'escola/configuracoes.html')
