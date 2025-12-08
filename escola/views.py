import json
import io
from decimal import Decimal, InvalidOperation
from django.db.models import Q, Count, Avg
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from rest_framework import viewsets
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from openpyxl import Workbook
from django.utils import timezone

from .models import (
    Aluno, Nota, Turma, Professor, Disciplina, 
    Aviso, Frequencia, Matricula, Evento, HorarioAula, Curso, Documento, Material,
    JustificativaFalta
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
        return redirect('dashboard_admin')
    
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


def pagina_institucional(request):
    return render(request, 'escola/institucional.html')


def pagina_plataforma(request):
    return render(request, 'escola/plataforma.html')


def pagina_juridico(request):
    return render(request, 'escola/juridico.html')


@login_required
def dashboard_aluno(request):
    try:
        aluno = request.user.perfil_aluno
        media_geral = aluno.calcular_media_geral()
        faltas_totais = aluno.contar_faltas()
    except AttributeError:
        messages.error(request, 'Perfil de aluno não encontrado.')
        return redirect('home')

    avisos_query = Q(destinatario='todos') | Q(destinatario='alunos')
    if aluno.turma_atual:
        avisos_query = avisos_query | (Q(destinatario='turma') & Q(turma=aluno.turma_atual))
    
    avisos = Aviso.objects.filter(avisos_query, ativo=True).order_by('-data_criacao')[:5]

    desempenho_data = []
    if aluno.turma_atual:
        for disciplina in aluno.turma_atual.curso.disciplinas.all():
            notas = Nota.objects.filter(matricula__aluno=aluno, disciplina=disciplina)
            lista_notas = [float(n.valor) for n in notas]
            media = round(sum(lista_notas) / len(lista_notas), 1) if lista_notas else 0
            desempenho_data.append({
                'disciplina': disciplina.nome[:15],
                'media': media
            })
    
    desempenho_json = json.dumps(desempenho_data)

    context = {
        'aluno': aluno,
        'media': media_geral,
        'faltas': faltas_totais,
        'avisos': avisos,
        'desempenho_json': desempenho_json,
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
        messages.error(request, 'Perfil de aluno não encontrado.')
        return redirect('home')
    
    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        justificativa_texto = request.POST.get('justificativa')
        documento = request.FILES.get('documento')
        
        if disciplina_id and data_inicio and data_fim and justificativa_texto:
            try:
                disciplina = Disciplina.objects.get(id=disciplina_id)
                justificativa = JustificativaFalta.objects.create(
                    aluno=aluno,
                    disciplina=disciplina,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    justificativa=justificativa_texto,
                    documento=documento
                )
                messages.success(request, 'Justificativa enviada com sucesso! Aguarde a análise da secretaria.')
            except Disciplina.DoesNotExist:
                messages.error(request, 'Disciplina não encontrada.')
            except Exception as e:
                messages.error(request, f'Erro ao enviar justificativa: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        
        return redirect('aluno_justificativa')
    
    justificativas = JustificativaFalta.objects.filter(aluno=aluno).order_by('-data_solicitacao')
    
    context = {
        'aluno': aluno,
        'justificativas': justificativas,
    }
    return render(request, 'escola/aluno_justificativa.html', context)


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
        
        elif action == 'atualizar_foto':
            if aluno and 'foto' in request.FILES:
                aluno.foto = request.FILES['foto']
                aluno.save()
                messages.success(request, 'Foto atualizada com sucesso!')
            else:
                messages.error(request, 'Selecione uma foto para enviar.')
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
def aluno_materiais(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        messages.error(request, 'Perfil de aluno não encontrado.')
        return redirect('home')
    
    materiais = []
    if aluno.turma_atual:
        materiais = Material.objects.filter(
            Q(turma=aluno.turma_atual) | Q(turma__isnull=True),
            disciplina__in=aluno.turma_atual.curso.disciplinas.all(),
            ativo=True
        ).select_related('disciplina', 'professor').order_by('-data_upload')
    
    disciplinas = []
    if aluno.turma_atual:
        disciplinas = aluno.turma_atual.curso.disciplinas.all()
    
    disciplina_filtro = request.GET.get('disciplina', '')
    tipo_filtro = request.GET.get('tipo', '')
    
    if disciplina_filtro:
        materiais = materiais.filter(disciplina_id=disciplina_filtro)
    if tipo_filtro:
        materiais = materiais.filter(tipo=tipo_filtro)
    
    context = {
        'aluno': aluno,
        'materiais': materiais,
        'disciplinas': disciplinas,
        'disciplina_filtro': disciplina_filtro,
        'tipo_filtro': tipo_filtro,
        'tipos_material': Material.TIPO_CHOICES,
    }
    return render(request, 'escola/aluno_materiais.html', context)


@login_required
def aluno_documentos(request):
    try:
        aluno = request.user.perfil_aluno
    except AttributeError:
        messages.error(request, 'Perfil de aluno não encontrado.')
        return redirect('home')
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao', '')
        
        if tipo:
            Documento.objects.create(
                aluno=aluno,
                tipo=tipo,
                descricao=descricao,
                criado_por=request.user
            )
            messages.success(request, 'Solicitação de documento enviada com sucesso!')
        else:
            messages.error(request, 'Selecione o tipo de documento.')
        
        return redirect('aluno_documentos')
    
    documentos = Documento.objects.filter(aluno=aluno).order_by('-data_solicitacao')
    
    context = {
        'aluno': aluno,
        'documentos': documentos,
        'tipos_documento': Documento.TIPOS_CHOICES,
    }
    return render(request, 'escola/aluno_documentos.html', context)


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
    justificativas_pendentes = JustificativaFalta.objects.filter(status='PENDENTE').count()

    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'total_cursos': total_cursos,
        'ultimos_alunos': ultimos_alunos,
        'documentos_pendentes': documentos_pendentes,
        'justificativas_pendentes': justificativas_pendentes,
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
    disciplinas = Disciplina.objects.all()
    return render(request, 'escola/secre_professores.html', {
        'professores': professores,
        'disciplinas': disciplinas
    })


@login_required
def secretaria_professor_adicionar(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    disciplinas = Disciplina.objects.all()
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        especialidade = request.POST.get('especialidade')
        data_admissao = request.POST.get('data_admissao')
        username = request.POST.get('username')
        password = request.POST.get('password')
        disciplinas_ids = request.POST.getlist('disciplinas')
        turmas_ids = request.POST.getlist('turmas')
        
        if nome and email and data_admissao:
            try:
                professor = Professor(
                    nome=nome,
                    email=email,
                    telefone=telefone,
                    especialidade=especialidade,
                    data_admissao=data_admissao
                )
                
                if 'foto' in request.FILES:
                    professor.foto = request.FILES['foto']
                
                if username and password:
                    if User.objects.filter(username=username).exists():
                        messages.error(request, 'Este nome de usuário já está em uso.')
                        return render(request, 'escola/secre_professor_form.html', {
                            'disciplinas': disciplinas,
                            'turmas': turmas,
                            'acao': 'Adicionar'
                        })
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=nome.split()[0] if nome else '',
                        last_name=' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                    )
                    professor.user = user
                
                professor.save()
                
                if disciplinas_ids:
                    professor.disciplinas.set(disciplinas_ids)
                if turmas_ids:
                    professor.turmas.set(turmas_ids)
                
                messages.success(request, f'Professor {nome} cadastrado com sucesso!')
                return redirect('secretaria_professores')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar professor: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/secre_professor_form.html', {
        'disciplinas': disciplinas,
        'turmas': turmas,
        'acao': 'Adicionar'
    })


@login_required
def secretaria_professor_editar(request, professor_id):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    professor = get_object_or_404(Professor, id=professor_id)
    disciplinas = Disciplina.objects.all()
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        professor.nome = request.POST.get('nome')
        professor.email = request.POST.get('email')
        professor.telefone = request.POST.get('telefone')
        professor.especialidade = request.POST.get('especialidade')
        professor.data_admissao = request.POST.get('data_admissao')
        
        if 'foto' in request.FILES:
            professor.foto = request.FILES['foto']
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        disciplinas_ids = request.POST.getlist('disciplinas')
        turmas_ids = request.POST.getlist('turmas')
        
        try:
            if username:
                if professor.user:
                    if professor.user.username != username:
                        if User.objects.filter(username=username).exclude(id=professor.user.id).exists():
                            messages.error(request, 'Este nome de usuário já está em uso.')
                            return render(request, 'escola/secre_professor_form.html', {
                                'disciplinas': disciplinas,
                                'turmas': turmas,
                                'professor': professor, 
                                'acao': 'Editar'
                            })
                        professor.user.username = username
                    if password:
                        professor.user.set_password(password)
                    professor.user.email = professor.email
                    professor.user.save()
                else:
                    if User.objects.filter(username=username).exists():
                        messages.error(request, 'Este nome de usuário já está em uso.')
                        return render(request, 'escola/secre_professor_form.html', {
                            'disciplinas': disciplinas,
                            'turmas': turmas,
                            'professor': professor, 
                            'acao': 'Editar'
                        })
                    if not password:
                        messages.error(request, 'Por favor, informe uma senha para criar o usuário.')
                        return render(request, 'escola/secre_professor_form.html', {
                            'disciplinas': disciplinas,
                            'turmas': turmas,
                            'professor': professor, 
                            'acao': 'Editar'
                        })
                    user = User.objects.create_user(
                        username=username,
                        email=professor.email,
                        password=password,
                        first_name=professor.nome.split()[0] if professor.nome else '',
                        last_name=' '.join(professor.nome.split()[1:]) if professor.nome and len(professor.nome.split()) > 1 else ''
                    )
                    professor.user = user
            
            professor.save()
            
            professor.disciplinas.set(disciplinas_ids)
            professor.turmas.set(turmas_ids)
            
            messages.success(request, f'Professor {professor.nome} atualizado com sucesso!')
            return redirect('secretaria_professores')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar professor: {str(e)}')
    
    return render(request, 'escola/secre_professor_form.html', {
        'disciplinas': disciplinas,
        'turmas': turmas,
        'professor': professor, 
        'acao': 'Editar'
    })


@login_required
def secretaria_professor_excluir(request, professor_id):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    professor = get_object_or_404(Professor, id=professor_id)
    
    if request.method == 'POST':
        nome = professor.nome
        if professor.user:
            professor.user.delete()
        professor.delete()
        messages.success(request, f'Professor {nome} excluído com sucesso!')
        return redirect('secretaria_professores')
    
    return render(request, 'escola/secre_professor_excluir.html', {'professor': professor})


@login_required
def secretaria_academico(request):
    if not check_secretaria_permission(request.user):
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        entity = request.POST.get('entity')
        
        if action == 'adicionar_curso':
            nome = request.POST.get('nome')
            codigo = request.POST.get('codigo')
            descricao = request.POST.get('descricao', '')
            carga_horaria = request.POST.get('carga_horaria', 0)
            if nome and codigo:
                try:
                    Curso.objects.create(
                        nome=nome,
                        codigo=codigo,
                        descricao=descricao,
                        carga_horaria=int(carga_horaria) if carga_horaria else 0
                    )
                    messages.success(request, f'Curso "{nome}" criado com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar curso: {str(e)}')
            else:
                messages.error(request, 'Preencha nome e código do curso.')
        
        elif action == 'editar_curso':
            curso_id = request.POST.get('curso_id')
            nome = request.POST.get('nome')
            codigo = request.POST.get('codigo')
            descricao = request.POST.get('descricao', '')
            carga_horaria = request.POST.get('carga_horaria', 0)
            try:
                curso = Curso.objects.get(id=curso_id)
                curso.nome = nome
                curso.codigo = codigo
                curso.descricao = descricao
                curso.carga_horaria = int(carga_horaria) if carga_horaria else 0
                curso.save()
                messages.success(request, f'Curso "{nome}" atualizado com sucesso!')
            except Curso.DoesNotExist:
                messages.error(request, 'Curso não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar curso: {str(e)}')
        
        elif action == 'excluir_curso':
            curso_id = request.POST.get('curso_id')
            try:
                curso = Curso.objects.get(id=curso_id)
                nome = curso.nome
                curso.delete()
                messages.success(request, f'Curso "{nome}" excluído com sucesso!')
            except Curso.DoesNotExist:
                messages.error(request, 'Curso não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro ao excluir curso: {str(e)}')
        
        elif action == 'adicionar_turma':
            codigo = request.POST.get('codigo')
            semestre = request.POST.get('semestre')
            turno = request.POST.get('turno')
            curso_id = request.POST.get('curso_id')
            professores_ids = request.POST.getlist('professores')
            if codigo and semestre and turno and curso_id:
                try:
                    from django.db import transaction
                    with transaction.atomic():
                        curso = Curso.objects.get(id=curso_id)
                        turma = Turma.objects.create(
                            codigo=codigo,
                            semestre=semestre,
                            turno=turno,
                            curso=curso
                        )
                        
                        if professores_ids:
                            professors_to_assign = Professor.objects.filter(id__in=professores_ids)
                            for professor in professors_to_assign:
                                professor.turmas.add(turma)
                        
                        messages.success(request, f'Turma "{codigo}" criada com sucesso!')
                except Curso.DoesNotExist:
                    messages.error(request, 'Curso não encontrado.')
                except Exception as e:
                    messages.error(request, f'Erro ao criar turma: {str(e)}')
            else:
                messages.error(request, 'Preencha todos os campos obrigatórios.')
        
        elif action == 'editar_turma':
            turma_id = request.POST.get('turma_id')
            codigo = request.POST.get('codigo')
            semestre = request.POST.get('semestre')
            turno = request.POST.get('turno')
            curso_id = request.POST.get('curso_id')
            professores_ids = request.POST.getlist('professores')
            try:
                from django.db import transaction
                with transaction.atomic():
                    turma = Turma.objects.get(id=turma_id)
                    curso = Curso.objects.get(id=curso_id)
                    turma.codigo = codigo
                    turma.semestre = semestre
                    turma.turno = turno
                    turma.curso = curso
                    turma.save()
                    
                    current_professors = set(turma.professores.values_list('id', flat=True))
                    new_professors = set(int(pid) for pid in professores_ids if pid)
                    
                    to_remove = current_professors - new_professors
                    to_add = new_professors - current_professors
                    
                    for professor in Professor.objects.filter(id__in=to_remove):
                        professor.turmas.remove(turma)
                    for professor in Professor.objects.filter(id__in=to_add):
                        professor.turmas.add(turma)
                    
                    messages.success(request, f'Turma "{codigo}" atualizada com sucesso!')
            except (Turma.DoesNotExist, Curso.DoesNotExist):
                messages.error(request, 'Turma ou curso não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar turma: {str(e)}')
        
        elif action == 'excluir_turma':
            turma_id = request.POST.get('turma_id')
            try:
                turma = Turma.objects.get(id=turma_id)
                codigo = turma.codigo
                turma.delete()
                messages.success(request, f'Turma "{codigo}" excluída com sucesso!')
            except Turma.DoesNotExist:
                messages.error(request, 'Turma não encontrada.')
            except Exception as e:
                messages.error(request, f'Erro ao excluir turma: {str(e)}')
        
        elif action == 'adicionar_disciplina':
            nome = request.POST.get('nome')
            ementa = request.POST.get('ementa', '')
            curso_id = request.POST.get('curso_id')
            if nome and curso_id:
                try:
                    curso = Curso.objects.get(id=curso_id)
                    Disciplina.objects.create(
                        nome=nome,
                        ementa=ementa,
                        curso=curso
                    )
                    messages.success(request, f'Disciplina "{nome}" criada com sucesso!')
                except Curso.DoesNotExist:
                    messages.error(request, 'Curso não encontrado.')
                except Exception as e:
                    messages.error(request, f'Erro ao criar disciplina: {str(e)}')
            else:
                messages.error(request, 'Preencha nome e curso da disciplina.')
        
        elif action == 'editar_disciplina':
            disciplina_id = request.POST.get('disciplina_id')
            nome = request.POST.get('nome')
            ementa = request.POST.get('ementa', '')
            curso_id = request.POST.get('curso_id')
            try:
                disciplina = Disciplina.objects.get(id=disciplina_id)
                curso = Curso.objects.get(id=curso_id)
                disciplina.nome = nome
                disciplina.ementa = ementa
                disciplina.curso = curso
                disciplina.save()
                messages.success(request, f'Disciplina "{nome}" atualizada com sucesso!')
            except (Disciplina.DoesNotExist, Curso.DoesNotExist):
                messages.error(request, 'Disciplina ou curso não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar disciplina: {str(e)}')
        
        elif action == 'excluir_disciplina':
            disciplina_id = request.POST.get('disciplina_id')
            try:
                disciplina = Disciplina.objects.get(id=disciplina_id)
                nome = disciplina.nome
                disciplina.delete()
                messages.success(request, f'Disciplina "{nome}" excluída com sucesso!')
            except Disciplina.DoesNotExist:
                messages.error(request, 'Disciplina não encontrada.')
            except Exception as e:
                messages.error(request, f'Erro ao excluir disciplina: {str(e)}')
        
        return redirect('secretaria_academico')
    
    cursos = Curso.objects.annotate(total_turmas=Count('turma'))
    turmas = Turma.objects.annotate(total_alunos=Count('alunos_turma')).select_related('curso').prefetch_related('professores')
    disciplinas = Disciplina.objects.select_related('curso')
    professores = Professor.objects.all()
    
    context = {
        'cursos': cursos,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'professores': professores
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
def secretaria_documento_visualizar(request, doc_id):
    if not check_secretaria_permission(request.user):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')
    
    try:
        documento = Documento.objects.select_related('aluno').get(id=doc_id)
        return JsonResponse({
            'success': True,
            'documento': {
                'id': documento.id,
                'tipo': documento.get_tipo_display(),
                'aluno': documento.aluno.nome,
                'matricula': documento.aluno.matricula,
                'turma': documento.aluno.turma_atual.codigo if documento.aluno.turma_atual else '-',
                'data_solicitacao': documento.data_solicitacao.strftime('%d/%m/%Y %H:%M') if documento.data_solicitacao else '-',
                'data_emissao': documento.data_emissao.strftime('%d/%m/%Y %H:%M') if documento.data_emissao else '-',
                'status': documento.get_status_display(),
                'descricao': documento.descricao or '',
                'arquivo_url': documento.arquivo.url if documento.arquivo else None,
            }
        })
    except Documento.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Documento não encontrado.'})


@login_required
def secretaria_documento_emitir(request, doc_id):
    if not check_secretaria_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Acesso não autorizado.'})
    
    if request.method == 'POST':
        try:
            documento = Documento.objects.get(id=doc_id)
            if documento.status == 'PENDENTE':
                documento.status = 'EMITIDO'
                documento.data_emissao = timezone.now()
                if request.FILES.get('arquivo'):
                    documento.arquivo = request.FILES.get('arquivo')
                documento.save()
                return JsonResponse({'success': True, 'message': 'Documento emitido com sucesso!'})
            else:
                return JsonResponse({'success': False, 'error': 'Documento já foi emitido.'})
        except Documento.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Documento não encontrado.'})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido.'})


@login_required
def secretaria_documento_confirmar(request, doc_id):
    if not check_secretaria_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Acesso não autorizado.'})
    
    if request.method == 'POST':
        try:
            documento = Documento.objects.get(id=doc_id)
            if documento.status == 'EMITIDO':
                documento.status = 'ENTREGUE'
                documento.save()
                return JsonResponse({'success': True, 'message': 'Entrega confirmada com sucesso!'})
            else:
                return JsonResponse({'success': False, 'error': 'Documento precisa estar emitido para confirmar entrega.'})
        except Documento.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Documento não encontrado.'})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido.'})


@login_required
def secretaria_documento_enviar(request, doc_id):
    if not check_secretaria_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Acesso não autorizado.'})
    
    if request.method == 'POST':
        try:
            documento = Documento.objects.get(id=doc_id)
            if documento.status in ['EMITIDO', 'ENTREGUE']:
                if request.FILES.get('arquivo'):
                    documento.arquivo = request.FILES.get('arquivo')
                    documento.save()
                    return JsonResponse({'success': True, 'message': 'Documento enviado com sucesso! O aluno ja pode fazer o download.'})
                else:
                    return JsonResponse({'success': False, 'error': 'Nenhum arquivo selecionado.'})
            else:
                return JsonResponse({'success': False, 'error': 'Documento precisa estar emitido ou entregue para enviar arquivo.'})
        except Documento.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Documento não encontrado.'})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido.'})


@login_required
def aluno_documento_download(request, doc_id):
    if not hasattr(request.user, 'perfil_aluno'):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')
    
    try:
        aluno = request.user.perfil_aluno
        documento = Documento.objects.get(id=doc_id, aluno=aluno)
        
        if documento.arquivo and documento.status in ['EMITIDO', 'ENTREGUE']:
            response = FileResponse(documento.arquivo.open('rb'), as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{documento.get_tipo_display()}_{aluno.matricula}.pdf"'
            return response
        else:
            messages.error(request, "Documento ainda não está disponível para download.")
            return redirect('aluno_documentos')
    except Documento.DoesNotExist:
        messages.error(request, "Documento não encontrado.")
        return redirect('aluno_documentos')


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
def secretaria_evento_adicionar(request):
    if not check_secretaria_permission(request.user):
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
            return redirect('secretaria_calendario')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/secre_evento_form.html', {
        'turmas': turmas,
        'tipos': Evento.TIPO_CHOICES,
        'acao': 'Adicionar'
    })


@login_required
def secretaria_evento_editar(request, evento_id):
    if not check_secretaria_permission(request.user):
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
        messages.success(request, f'Evento "{evento.titulo}" atualizado!')
        return redirect('secretaria_calendario')
    
    return render(request, 'escola/secre_evento_form.html', {
        'turmas': turmas,
        'tipos': Evento.TIPO_CHOICES,
        'evento': evento,
        'acao': 'Editar'
    })


@login_required
def secretaria_evento_excluir(request, evento_id):
    if not check_secretaria_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    evento = get_object_or_404(Evento, id=evento_id)
    titulo = evento.titulo
    evento.delete()
    messages.success(request, f'Evento "{titulo}" excluído com sucesso!')
    return redirect('secretaria_calendario')


@login_required
def secretaria_justificativas(request):
    if not check_secretaria_permission(request.user):
        messages.error(request, "Acesso não autorizado.")
        return redirect('home')

    status_filtro = request.GET.get('status', '')
    busca_aluno = request.GET.get('aluno', '')

    justificativas = JustificativaFalta.objects.select_related('aluno', 'disciplina').order_by('-data_solicitacao')

    if status_filtro:
        justificativas = justificativas.filter(status=status_filtro)

    if busca_aluno:
        justificativas = justificativas.filter(aluno__nome__icontains=busca_aluno)

    if request.method == 'POST':
        justificativa_id = request.POST.get('justificativa_id')
        acao = request.POST.get('acao')
        observacao = request.POST.get('observacao', '')

        if justificativa_id and acao:
            try:
                justificativa = JustificativaFalta.objects.get(id=justificativa_id)
                if acao == 'aprovar':
                    justificativa.status = 'APROVADA'
                elif acao == 'rejeitar':
                    justificativa.status = 'REJEITADA'
                justificativa.observacao = observacao
                justificativa.data_analise = timezone.now()
                justificativa.analisado_por = request.user
                justificativa.save()
                messages.success(request, f'Justificativa {acao}da com sucesso!')
            except JustificativaFalta.DoesNotExist:
                messages.error(request, 'Justificativa não encontrada.')
        return redirect('secretaria_justificativas')

    pendentes = justificativas.filter(status='PENDENTE').count()

    context = {
        'justificativas': justificativas,
        'status_filtro': status_filtro,
        'busca_aluno': busca_aluno,
        'pendentes': pendentes,
    }
    return render(request, 'escola/secre_justificativas.html', context)


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
    alunos_turma = []
    media_turma = None
    frequencia_turma = None
    
    if turma_id:
        try:
            turma_selecionada = Turma.objects.annotate(
                total_alunos=Count('alunos_turma')
            ).get(id=turma_id)
            
            alunos_turma = Aluno.objects.filter(turma_atual=turma_selecionada).order_by('nome')
            
            alunos_com_media = []
            total_media = Decimal('0')
            total_frequencia = 0
            count_alunos = 0
            count_freq = 0
            
            for aluno in alunos_turma:
                notas = Nota.objects.filter(matricula__aluno=aluno)
                if notas.exists():
                    media = notas.aggregate(avg=Avg('valor'))['avg']
                    media = round(float(media), 1) if media else 0
                else:
                    media = 0
                
                frequencias = Frequencia.objects.filter(matricula__aluno=aluno)
                total_aulas = frequencias.count()
                presencas = frequencias.filter(presente=True).count()
                freq_percent = int((presencas / total_aulas) * 100) if total_aulas > 0 else 100
                
                alunos_com_media.append({
                    'aluno': aluno,
                    'media': media,
                    'frequencia': freq_percent,
                    'status': 'Aprovado' if media >= 6 else ('Recuperação' if media > 0 else 'Cursando')
                })
                
                if media > 0:
                    total_media += Decimal(str(media))
                    count_alunos += 1
                if total_aulas > 0:
                    total_frequencia += freq_percent
                    count_freq += 1
            
            alunos_turma = alunos_com_media
            media_turma = round(float(total_media / count_alunos), 1) if count_alunos > 0 else None
            frequencia_turma = int(total_frequencia / count_freq) if count_freq > 0 else None
            
        except Turma.DoesNotExist:
            pass
    
    total_alunos = Aluno.objects.count()
    
    all_notas = Nota.objects.all()
    media_geral = None
    if all_notas.exists():
        avg = all_notas.aggregate(avg=Avg('valor'))['avg']
        media_geral = round(float(avg), 1) if avg else None
    
    total_freq = Frequencia.objects.count()
    presencas_total = Frequencia.objects.filter(presente=True).count()
    frequencia_media = int((presencas_total / total_freq) * 100) if total_freq > 0 else None
    
    context = {
        'turmas': turmas,
        'turma_selecionada': turma_selecionada,
        'total_alunos': total_alunos,
        'alunos_turma': alunos_turma,
        'media_turma': media_turma,
        'frequencia_turma': frequencia_turma,
        'media_geral': media_geral,
        'frequencia_media': frequencia_media,
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
def coordenacao_horarios(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    turmas = Turma.objects.all().order_by('codigo')
    disciplinas = Disciplina.objects.all().order_by('nome')
    turma_id = request.GET.get('turma')
    turma_selecionada = None
    horarios = []
    
    dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    horarios_padrao = ['07:00', '07:50', '08:40', '09:30', '09:50', '10:40', '11:30']
    
    if turma_id:
        try:
            turma_selecionada = Turma.objects.get(id=turma_id)
            aulas = HorarioAula.objects.filter(turma=turma_selecionada).select_related('disciplina')
            
            for hora in horarios_padrao:
                linha = {'hora': hora, 'aulas': {}}
                for dia in dias:
                    aula = aulas.filter(dia_semana=dia, hora_inicio__hour=int(hora.split(':')[0]), 
                                       hora_inicio__minute=int(hora.split(':')[1])).first()
                    linha['aulas'][dia] = aula
                horarios.append(linha)
        except Turma.DoesNotExist:
            pass
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'salvar':
            turma_post_id = request.POST.get('turma_id')
            dia = request.POST.get('dia')
            hora = request.POST.get('hora')
            disciplina_id = request.POST.get('disciplina_id')
            
            if turma_post_id and dia and hora:
                from datetime import datetime, time, timedelta
                turma_obj = get_object_or_404(Turma, id=turma_post_id)
                hora_parts = hora.split(':')
                hora_inicio = time(int(hora_parts[0]), int(hora_parts[1]))
                hora_fim_dt = datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=50)
                hora_fim = hora_fim_dt.time()
                
                HorarioAula.objects.filter(turma=turma_obj, dia_semana=dia, hora_inicio=hora_inicio).delete()
                
                if disciplina_id:
                    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
                    HorarioAula.objects.create(
                        turma=turma_obj,
                        disciplina=disciplina,
                        dia_semana=dia,
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim
                    )
                    messages.success(request, 'Horário salvo com sucesso!')
                else:
                    messages.success(request, 'Horário removido com sucesso!')
                
                return redirect(f"{request.path}?turma={turma_post_id}")
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'turma_selecionada': turma_selecionada,
        'horarios': horarios,
        'dias': dias,
        'horarios_padrao': horarios_padrao,
    }
    return render(request, 'escola/coor_horarios.html', context)


@login_required
def coordenacao_cursos(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    cursos = Curso.objects.annotate(
        total_turmas=Count('turma'),
        total_disciplinas=Count('disciplinas')
    ).order_by('nome')
    
    context = {
        'cursos': cursos,
    }
    return render(request, 'escola/coor_cursos.html', context)


@login_required
def coordenacao_curso_adicionar(request):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        descricao = request.POST.get('descricao')
        carga_horaria = request.POST.get('carga_horaria')
        
        if nome and codigo and carga_horaria:
            try:
                Curso.objects.create(
                    nome=nome,
                    codigo=codigo,
                    descricao=descricao,
                    carga_horaria=int(carga_horaria)
                )
                messages.success(request, f'Curso "{nome}" criado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao criar curso: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return redirect('coordenacao_cursos')


@login_required
def coordenacao_curso_editar(request, curso_id):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    curso = get_object_or_404(Curso, id=curso_id)
    
    if request.method == 'POST':
        curso.nome = request.POST.get('nome')
        curso.codigo = request.POST.get('codigo')
        curso.descricao = request.POST.get('descricao')
        carga_horaria = request.POST.get('carga_horaria')
        if carga_horaria:
            curso.carga_horaria = int(carga_horaria)
        
        try:
            curso.save()
            messages.success(request, f'Curso "{curso.nome}" atualizado!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
    
    return redirect('coordenacao_cursos')


@login_required
def coordenacao_curso_excluir(request, curso_id):
    if not check_coordenacao_permission(request.user):
        return redirect('home')
    
    curso = get_object_or_404(Curso, id=curso_id)
    
    if request.method == 'POST':
        nome = curso.nome
        try:
            curso.delete()
            messages.success(request, f'Curso "{nome}" excluído!')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir: curso possui turmas vinculadas.')
    
    return redirect('coordenacao_cursos')


@login_required
def coordenacao_professor_senha(request, professor_id):
    if not check_coordenacao_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    professor = get_object_or_404(Professor, id=professor_id)
    
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        
        if nova_senha and len(nova_senha) >= 6:
            if professor.user:
                professor.user.set_password(nova_senha)
                professor.user.save()
                messages.success(request, f'Senha do professor {professor.nome} alterada com sucesso!')
            else:
                username = professor.email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{professor.id}"
                user = User.objects.create_user(
                    username=username,
                    email=professor.email,
                    password=nova_senha,
                    first_name=professor.nome.split()[0] if professor.nome else '',
                    last_name=' '.join(professor.nome.split()[1:]) if professor.nome and len(professor.nome.split()) > 1 else ''
                )
                professor.user = user
                professor.save()
                messages.success(request, f'Usuário criado e senha definida para {professor.nome}!')
        else:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
    
    return redirect('coordenacao_professores')


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
        turmas = professor.turmas.annotate(total_alunos=Count('alunos_turma'))
    
    avisos = Aviso.objects.filter(
        Q(destinatario='todos') | Q(destinatario='professores')
    ).order_by('-data_criacao')[:3]
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
    
    professor = getattr(request.user, 'perfil_professor', None)
    
    if professor:
        turmas = professor.turmas.all()
        disciplinas = professor.disciplinas.all()
    else:
        turmas = Turma.objects.none()
        disciplinas = Disciplina.objects.none()
    
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    
    alunos = []
    turma_selecionada = None
    disciplina_selecionada = None
    
    if turma_id:
        turma_selecionada = turmas.filter(id=turma_id).first()
        if turma_selecionada:
            alunos = Aluno.objects.filter(turma_atual=turma_selecionada).order_by('nome')
            
            if disciplina_id:
                disciplina_selecionada = disciplinas.filter(id=disciplina_id).first()
                if disciplina_selecionada:
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
        professor = getattr(request.user, 'perfil_professor', None)
        if not professor:
            messages.error(request, 'Perfil de professor não encontrado.')
            return redirect('professor_notas')
        
        turma_id = request.POST.get('turma_id')
        disciplina_id = request.POST.get('disciplina_id')
        tipo_avaliacao = request.POST.get('tipo_avaliacao', 'Prova')
        
        turma = professor.turmas.filter(id=turma_id).first()
        disciplina = professor.disciplinas.filter(id=disciplina_id).first()
        
        if not turma or not disciplina:
            messages.error(request, 'Você não tem permissão para acessar esta turma ou disciplina.')
            return redirect('professor_notas')
        
        notas_salvas = 0
        notas_atualizadas = 0
        notas_invalidas = 0
        notas_vazias = 0
        
        for key, value in request.POST.items():
            if key.startswith('nota_'):
                aluno_id = key.replace('nota_', '')
                try:
                    if not value or not value.strip():
                        notas_vazias += 1
                        continue
                    
                    nota_valor = Decimal(value.strip().replace(',', '.'))
                    if nota_valor < 0 or nota_valor > 10:
                        notas_invalidas += 1
                        continue
                    
                    aluno = Aluno.objects.get(id=aluno_id)
                    matricula = Matricula.objects.filter(aluno=aluno, turma=turma).first()
                    
                    if not matricula:
                        if aluno.turma_atual == turma:
                            matricula = Matricula.objects.create(
                                aluno=aluno,
                                turma=turma,
                                status='Ativo'
                            )
                        else:
                            notas_invalidas += 1
                            continue
                    
                    nota, created = Nota.objects.update_or_create(
                        matricula=matricula,
                        disciplina=disciplina,
                        tipo_avaliacao=tipo_avaliacao,
                        defaults={'valor': nota_valor}
                    )
                    if created:
                        notas_salvas += 1
                    else:
                        notas_atualizadas += 1
                except (Aluno.DoesNotExist, ValueError, InvalidOperation):
                    notas_invalidas += 1
                    continue
        
        if notas_salvas > 0 or notas_atualizadas > 0:
            msg = f'Notas processadas: {notas_salvas} novas, {notas_atualizadas} atualizadas.'
            if notas_invalidas > 0:
                msg += f' ({notas_invalidas} valores inválidos foram ignorados - use valores entre 0 e 10)'
            messages.success(request, msg)
        elif notas_invalidas > 0:
            messages.warning(request, f'{notas_invalidas} notas foram rejeitadas por valores inválidos. Use valores entre 0 e 10.')
        else:
            messages.info(request, 'Nenhuma nota foi informada para salvar.')
        return redirect('professor_notas')
    
    return redirect('professor_notas')


@login_required
def professor_frequencia(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    professor = getattr(request.user, 'perfil_professor', None)
    
    if professor:
        turmas = professor.turmas.all()
        disciplinas = professor.disciplinas.all()
    else:
        turmas = Turma.objects.none()
        disciplinas = Disciplina.objects.none()
    
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    data = request.GET.get('data', timezone.now().strftime('%Y-%m-%d'))
    
    alunos = []
    turma_selecionada = None
    disciplina_selecionada = None
    
    if turma_id:
        turma_selecionada = turmas.filter(id=turma_id).first()
        if turma_selecionada:
            alunos = Aluno.objects.filter(turma_atual=turma_selecionada).order_by('nome')
            
            if disciplina_id:
                disciplina_selecionada = disciplinas.filter(id=disciplina_id).first()
    
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
        professor = getattr(request.user, 'perfil_professor', None)
        if not professor:
            messages.error(request, 'Perfil de professor não encontrado.')
            return redirect('professor_frequencia')
        
        turma_id = request.POST.get('turma_id')
        disciplina_id = request.POST.get('disciplina_id')
        data_aula = request.POST.get('data_aula')
        
        turma = professor.turmas.filter(id=turma_id).first()
        disciplina = professor.disciplinas.filter(id=disciplina_id).first()
        
        if not turma or not disciplina:
            messages.error(request, 'Você não tem permissão para acessar esta turma ou disciplina.')
            return redirect('professor_frequencia')
        
        alunos = Aluno.objects.filter(turma_atual=turma)
        frequencias_salvas = 0
        alunos_sem_matricula = 0
        
        for aluno in alunos:
            matricula = Matricula.objects.filter(aluno=aluno, turma=turma).first()
            
            if not matricula:
                matricula = Matricula.objects.create(
                    aluno=aluno,
                    turma=turma,
                    status='Ativo'
                )
            
            presente = request.POST.get(f'presente_{aluno.id}') == 'on'
            
            Frequencia.objects.update_or_create(
                matricula=matricula,
                disciplina=disciplina,
                data_aula=data_aula,
                defaults={'presente': presente}
            )
            frequencias_salvas += 1
        
        msg = f'Frequência salva com sucesso! ({frequencias_salvas} alunos)'
        if alunos_sem_matricula > 0:
            msg += f' - {alunos_sem_matricula} aluno(s) sem matrícula foram ignorados.'
        messages.success(request, msg)
        return redirect('professor_frequencia')
    
    return redirect('professor_frequencia')


@login_required
def professor_materiais(request):
    if not check_professor_permission(request.user):
        return redirect('home')
    
    professor = getattr(request.user, 'perfil_professor', None)
    
    if professor:
        disciplinas = professor.disciplinas.all()
        turmas = professor.turmas.all()
    else:
        disciplinas = Disciplina.objects.none()
        turmas = Turma.objects.none()
    
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
    
    if professor:
        turmas = professor.turmas.all()
        eventos = Evento.objects.filter(
            Q(turma__isnull=True) | Q(turma__in=turmas)
        ).order_by('-data')
    else:
        turmas = Turma.objects.none()
        eventos = Evento.objects.none()
    
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
        
        elif action == 'atualizar_foto':
            if professor and 'foto' in request.FILES:
                professor.foto = request.FILES['foto']
                professor.save()
                messages.success(request, 'Foto atualizada com sucesso!')
            else:
                messages.error(request, 'Selecione uma foto para enviar.')
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if nome and email and cpf and matricula and data_nascimento:
            if username and User.objects.filter(username=username).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
                return render(request, 'escola/secre_aluno_form.html', {
                    'turmas': turmas, 
                    'acao': 'Adicionar'
                })
            
            if username and not password:
                messages.error(request, 'Por favor, informe uma senha para o usuário.')
                return render(request, 'escola/secre_aluno_form.html', {
                    'turmas': turmas, 
                    'acao': 'Adicionar'
                })
            
            try:
                from django.db import transaction
                
                with transaction.atomic():
                    aluno = Aluno(
                        nome=nome,
                        email=email,
                        cpf=cpf,
                        matricula=matricula,
                        data_nascimento=data_nascimento,
                        telefone=telefone
                    )
                    
                    if username and password:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=nome.split()[0] if nome else '',
                            last_name=' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                        )
                        aluno.user = user
                    
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
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        matricula_val = request.POST.get('matricula')
        data_nascimento = request.POST.get('data_nascimento')
        telefone = request.POST.get('telefone')
        turma_id = request.POST.get('turma_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username:
            if aluno.user:
                if aluno.user.username != username:
                    if User.objects.filter(username=username).exclude(id=aluno.user.id).exists():
                        messages.error(request, 'Este nome de usuário já está em uso.')
                        return render(request, 'escola/secre_aluno_form.html', {
                            'turmas': turmas, 
                            'aluno': aluno, 
                            'acao': 'Editar'
                        })
            else:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Este nome de usuário já está em uso.')
                    return render(request, 'escola/secre_aluno_form.html', {
                        'turmas': turmas, 
                        'aluno': aluno, 
                        'acao': 'Editar'
                    })
                if not password:
                    messages.error(request, 'Por favor, informe uma senha para criar o usuário.')
                    return render(request, 'escola/secre_aluno_form.html', {
                        'turmas': turmas, 
                        'aluno': aluno, 
                        'acao': 'Editar'
                    })
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                aluno.nome = nome
                aluno.email = email
                aluno.cpf = cpf
                aluno.matricula = matricula_val
                aluno.data_nascimento = data_nascimento
                aluno.telefone = telefone
                
                if 'foto' in request.FILES:
                    aluno.foto = request.FILES['foto']
                
                if turma_id:
                    aluno.turma_atual_id = turma_id
                else:
                    aluno.turma_atual = None
                
                if username:
                    if aluno.user:
                        aluno.user.username = username
                        if password:
                            aluno.user.set_password(password)
                        aluno.user.email = email
                        aluno.user.first_name = nome.split()[0] if nome else ''
                        aluno.user.last_name = ' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                        aluno.user.save()
                    else:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=nome.split()[0] if nome else '',
                            last_name=' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                        )
                        aluno.user = user
                
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
    professores = Professor.objects.all()
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        curso_id = request.POST.get('curso_id')
        semestre = request.POST.get('semestre')
        turno = request.POST.get('turno')
        professores_ids = request.POST.getlist('professores')
        
        if codigo and curso_id:
            try:
                from django.db import transaction
                with transaction.atomic():
                    turma = Turma(
                        codigo=codigo,
                        curso_id=curso_id,
                        semestre=semestre,
                        turno=turno
                    )
                    turma.save()
                    
                    if professores_ids:
                        professors_to_assign = Professor.objects.filter(id__in=professores_ids)
                        for professor in professors_to_assign:
                            professor.turmas.add(turma)
                    
                    messages.success(request, f'Turma {codigo} criada com sucesso!')
                    return redirect('coordenacao_turmas')
            except Exception as e:
                messages.error(request, f'Erro ao criar turma: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    return render(request, 'escola/coor_turma_form.html', {
        'cursos': cursos,
        'professores': professores,
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
    professores = Professor.objects.all()
    
    if request.method == 'POST':
        turma.codigo = request.POST.get('codigo')
        turma.curso_id = request.POST.get('curso_id')
        turma.semestre = request.POST.get('semestre')
        turma.turno = request.POST.get('turno')
        professores_ids = request.POST.getlist('professores')
        
        try:
            from django.db import transaction
            with transaction.atomic():
                turma.save()
                
                current_professors = set(turma.professores.values_list('id', flat=True))
                new_professors = set(int(pid) for pid in professores_ids if pid)
                
                to_remove = current_professors - new_professors
                to_add = new_professors - current_professors
                
                for professor in Professor.objects.filter(id__in=to_remove):
                    professor.turmas.remove(turma)
                for professor in Professor.objects.filter(id__in=to_add):
                    professor.turmas.add(turma)
                
                messages.success(request, f'Turma {turma.codigo} atualizada com sucesso!')
                return redirect('coordenacao_turmas')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar turma: {str(e)}')
    
    return render(request, 'escola/coor_turma_form.html', {
        'turma': turma,
        'cursos': cursos,
        'professores': professores,
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if nome and email and cpf and matricula and data_nascimento_str:
            if username and User.objects.filter(username=username).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
                return render(request, 'escola/coor_aluno_form.html', {
                    'turmas': turmas, 
                    'acao': 'Adicionar'
                })
            
            if username and not password:
                messages.error(request, 'Por favor, informe uma senha para o usuário.')
                return render(request, 'escola/coor_aluno_form.html', {
                    'turmas': turmas, 
                    'acao': 'Adicionar'
                })
            
            try:
                from django.db import transaction, IntegrityError
                from datetime import datetime
                
                with transaction.atomic():
                    data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                    
                    if username and password:
                        try:
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=password,
                                first_name=nome.split()[0] if nome else '',
                                last_name=' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                            )
                            aluno_group, _ = Group.objects.get_or_create(name='Aluno')
                            user.groups.add(aluno_group)
                        except IntegrityError:
                            raise ValueError('Erro ao criar usuário: dados duplicados.')
                        except Exception as user_error:
                            raise ValueError(f'Erro ao criar usuário: {str(user_error)}')
                    else:
                        user = None
                    
                    aluno = Aluno(
                        nome=nome,
                        email=email,
                        cpf=cpf,
                        matricula=matricula,
                        data_nascimento=data_nascimento,
                        telefone=telefone,
                        user=user
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
            except ValueError as ve:
                messages.error(request, str(ve))
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
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        matricula_val = request.POST.get('matricula')
        data_nascimento_str = request.POST.get('data_nascimento')
        telefone = request.POST.get('telefone')
        turma_id = request.POST.get('turma_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username:
            if aluno.user:
                if aluno.user.username != username:
                    if User.objects.filter(username=username).exclude(id=aluno.user.id).exists():
                        messages.error(request, 'Este nome de usuário já está em uso.')
                        return render(request, 'escola/coor_aluno_form.html', {
                            'turmas': turmas, 
                            'aluno': aluno, 
                            'acao': 'Editar'
                        })
            else:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Este nome de usuário já está em uso.')
                    return render(request, 'escola/coor_aluno_form.html', {
                        'turmas': turmas, 
                        'aluno': aluno, 
                        'acao': 'Editar'
                    })
                if not password:
                    messages.error(request, 'Por favor, informe uma senha para criar o usuário.')
                    return render(request, 'escola/coor_aluno_form.html', {
                        'turmas': turmas, 
                        'aluno': aluno, 
                        'acao': 'Editar'
                    })
        
        try:
            from django.db import transaction, IntegrityError
            from datetime import datetime
            
            with transaction.atomic():
                aluno.nome = nome
                aluno.email = email
                aluno.cpf = cpf
                aluno.matricula = matricula_val
                aluno.telefone = telefone
                
                if 'foto' in request.FILES:
                    aluno.foto = request.FILES['foto']
                
                if data_nascimento_str:
                    aluno.data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                
                if turma_id:
                    aluno.turma_atual_id = turma_id
                else:
                    aluno.turma_atual = None
                
                if username:
                    if aluno.user:
                        aluno.user.username = username
                        if password:
                            aluno.user.set_password(password)
                        aluno.user.email = email
                        aluno.user.first_name = nome.split()[0] if nome else ''
                        aluno.user.last_name = ' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                        aluno.user.save()
                    else:
                        try:
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=password,
                                first_name=nome.split()[0] if nome else '',
                                last_name=' '.join(nome.split()[1:]) if nome and len(nome.split()) > 1 else ''
                            )
                            aluno_group, _ = Group.objects.get_or_create(name='Aluno')
                            user.groups.add(aluno_group)
                            aluno.user = user
                        except IntegrityError:
                            raise ValueError('Erro ao criar usuário: dados duplicados.')
                        except Exception as user_error:
                            raise ValueError(f'Erro ao criar usuário: {str(user_error)}')
                
                aluno.save()
            
            messages.success(request, f'Aluno {aluno.nome} atualizado com sucesso!')
            return redirect('coordenacao_alunos')
        except ValueError as ve:
            messages.error(request, str(ve))
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if nome and email and data_admissao_str:
            if username and not password:
                messages.error(request, 'Por favor, informe uma senha para o usuário.')
                return redirect('coordenacao_professores')
            
            try:
                from datetime import datetime
                from django.db import transaction
                
                with transaction.atomic():
                    data_admissao = datetime.strptime(data_admissao_str, '%Y-%m-%d').date()
                    
                    professor = Professor(
                        nome=nome,
                        email=email,
                        telefone=telefone,
                        especialidade=especialidade,
                        data_admissao=data_admissao
                    )
                    
                    if 'foto' in request.FILES:
                        professor.foto = request.FILES['foto']
                    
                    if username and password:
                        from django.contrib.auth.models import User, Group
                        if User.objects.filter(username=username).exists():
                            messages.error(request, 'Este nome de usuário já está em uso.')
                            return redirect('coordenacao_professores')
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=nome.split()[0] if nome else '',
                            last_name=' '.join(nome.split()[1:]) if len(nome.split()) > 1 else ''
                        )
                        professor_group, _ = Group.objects.get_or_create(name='Professor')
                        user.groups.add(professor_group)
                        professor.user = user
                    
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
        
        if 'foto' in request.FILES:
            professor.foto = request.FILES['foto']
        
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


# ==========================================
# ADMIN CUSTOM VIEWS
# ==========================================

def check_admin_permission(user):
    return user.is_superuser


@login_required
def dashboard_admin(request):
    if not check_admin_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    from django.contrib.auth.models import User
    
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    total_cursos = Curso.objects.count()
    total_usuarios = User.objects.count()
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    ultimos_alunos = Aluno.objects.order_by('-id')[:5]
    ultimos_avisos = Aviso.objects.order_by('-data_criacao')[:5]
    proximos_eventos = Evento.objects.filter(data__gte=timezone.now().date()).order_by('data')[:5]
    documentos_recentes = Documento.objects.filter(status='PENDENTE').order_by('-data_solicitacao')[:5]
    
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'total_cursos': total_cursos,
        'total_usuarios': total_usuarios,
        'documentos_pendentes': documentos_pendentes,
        'ultimos_alunos': ultimos_alunos,
        'ultimos_avisos': ultimos_avisos,
        'proximos_eventos': proximos_eventos,
        'documentos_recentes': documentos_recentes,
    }
    
    return render(request, 'escola/admin_dashboard.html', context)


@login_required
def admin_usuarios(request):
    if not check_admin_permission(request.user):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    from django.contrib.auth.models import User, Group
    
    usuarios = User.objects.all().order_by('-date_joined')
    grupos = Group.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            is_superuser = request.POST.get('is_superuser') == 'on'
            grupo_id = request.POST.get('grupo')
            
            if username and password:
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    user.is_superuser = is_superuser
                    user.is_staff = is_superuser
                    if grupo_id:
                        grupo = Group.objects.get(id=grupo_id)
                        user.groups.add(grupo)
                    user.save()
                    messages.success(request, f'Usuário {username} criado com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar usuário: {str(e)}')
            else:
                messages.error(request, 'Usuário e senha são obrigatórios.')
        
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            new_password = request.POST.get('new_password')
            if new_password:
                user.set_password(new_password)
            user.save()
            messages.success(request, f'Usuário {user.username} atualizado!')
        
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            if user != request.user:
                user.delete()
                messages.success(request, 'Usuário excluído!')
            else:
                messages.error(request, 'Você não pode excluir seu próprio usuário.')
        
        return redirect('admin_usuarios')
    
    return render(request, 'escola/admin_usuarios.html', {
        'usuarios': usuarios,
        'grupos': grupos,
    })


@login_required
def admin_alunos(request):
    if not check_admin_permission(request.user):
        return redirect('home')
    
    alunos = Aluno.objects.all().order_by('nome')
    turmas = Turma.objects.all()
    
    busca = request.GET.get('busca', '')
    if busca:
        alunos = alunos.filter(Q(nome__icontains=busca) | Q(matricula__icontains=busca))
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            nome = request.POST.get('nome')
            matricula = request.POST.get('matricula')
            email = request.POST.get('email')
            cpf = request.POST.get('cpf')
            data_nascimento = request.POST.get('data_nascimento')
            telefone = request.POST.get('telefone')
            turma_id = request.POST.get('turma')
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if nome and matricula and email and cpf and data_nascimento:
                try:
                    aluno = Aluno.objects.create(
                        nome=nome,
                        matricula=matricula,
                        email=email,
                        cpf=cpf,
                        data_nascimento=data_nascimento,
                        telefone=telefone,
                        turma_atual_id=turma_id if turma_id else None
                    )
                    if username and password:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        aluno.user = user
                        aluno.save()
                    messages.success(request, f'Aluno {nome} cadastrado com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao cadastrar aluno: {str(e)}')
            else:
                messages.error(request, 'Preencha todos os campos obrigatórios.')
        
        elif action == 'edit':
            aluno_id = request.POST.get('aluno_id')
            aluno = get_object_or_404(Aluno, id=aluno_id)
            aluno.nome = request.POST.get('nome', aluno.nome)
            aluno.email = request.POST.get('email', aluno.email)
            aluno.telefone = request.POST.get('telefone', aluno.telefone)
            turma_id = request.POST.get('turma')
            aluno.turma_atual_id = turma_id if turma_id else None
            new_username = request.POST.get('username')
            new_password = request.POST.get('new_password')
            if aluno.user:
                if new_username and new_username != aluno.user.username:
                    aluno.user.username = new_username
                if new_password:
                    aluno.user.set_password(new_password)
                aluno.user.save()
            aluno.save()
            messages.success(request, f'Aluno {aluno.nome} atualizado!')
        
        elif action == 'delete':
            aluno_id = request.POST.get('aluno_id')
            aluno = get_object_or_404(Aluno, id=aluno_id)
            nome = aluno.nome
            if aluno.user:
                aluno.user.delete()
            aluno.delete()
            messages.success(request, f'Aluno {nome} excluído!')
        
        return redirect('admin_alunos')
    
    return render(request, 'escola/admin_alunos.html', {
        'alunos': alunos,
        'turmas': turmas,
        'busca': busca,
    })


@login_required
def admin_professores(request):
    if not check_admin_permission(request.user):
        return redirect('home')
    
    professores = Professor.objects.all().order_by('nome')
    disciplinas = Disciplina.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            telefone = request.POST.get('telefone')
            especialidade = request.POST.get('especialidade')
            data_admissao = request.POST.get('data_admissao')
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if nome and email and data_admissao:
                try:
                    professor = Professor.objects.create(
                        nome=nome,
                        email=email,
                        telefone=telefone,
                        especialidade=especialidade,
                        data_admissao=data_admissao
                    )
                    if username and password:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        professor.user = user
                        professor.save()
                    messages.success(request, f'Professor {nome} cadastrado com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao cadastrar professor: {str(e)}')
            else:
                messages.error(request, 'Preencha nome, email e data de admissão.')
        
        elif action == 'edit':
            professor_id = request.POST.get('professor_id')
            professor = get_object_or_404(Professor, id=professor_id)
            professor.nome = request.POST.get('nome', professor.nome)
            professor.email = request.POST.get('email', professor.email)
            professor.telefone = request.POST.get('telefone', professor.telefone)
            professor.especialidade = request.POST.get('especialidade', professor.especialidade)
            new_username = request.POST.get('username')
            new_password = request.POST.get('new_password')
            if professor.user:
                if new_username and new_username != professor.user.username:
                    professor.user.username = new_username
                if new_password:
                    professor.user.set_password(new_password)
                professor.user.save()
            professor.save()
            messages.success(request, f'Professor {professor.nome} atualizado!')
        
        elif action == 'delete':
            professor_id = request.POST.get('professor_id')
            professor = get_object_or_404(Professor, id=professor_id)
            nome = professor.nome
            if professor.user:
                professor.user.delete()
            professor.delete()
            messages.success(request, f'Professor {nome} excluído!')
        
        return redirect('admin_professores')
    
    return render(request, 'escola/admin_professores.html', {
        'professores': professores,
        'disciplinas': disciplinas,
    })


@login_required
def admin_turmas(request):
    if not check_admin_permission(request.user):
        return redirect('home')
    
    turmas = Turma.objects.annotate(total_alunos=Count('alunos_turma')).order_by('codigo')
    cursos = Curso.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            codigo = request.POST.get('codigo')
            semestre = request.POST.get('semestre')
            turno = request.POST.get('turno')
            curso_id = request.POST.get('curso')
            
            if codigo and semestre and turno and curso_id:
                try:
                    Turma.objects.create(
                        codigo=codigo,
                        semestre=semestre,
                        turno=turno,
                        curso_id=curso_id
                    )
                    messages.success(request, f'Turma {codigo} criada com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar turma: {str(e)}')
            else:
                messages.error(request, 'Preencha todos os campos.')
        
        elif action == 'edit':
            turma_id = request.POST.get('turma_id')
            turma = get_object_or_404(Turma, id=turma_id)
            turma.codigo = request.POST.get('codigo', turma.codigo)
            turma.semestre = request.POST.get('semestre', turma.semestre)
            turma.turno = request.POST.get('turno', turma.turno)
            curso_id = request.POST.get('curso')
            if curso_id:
                turma.curso_id = curso_id
            turma.save()
            messages.success(request, f'Turma {turma.codigo} atualizada!')
        
        elif action == 'delete':
            turma_id = request.POST.get('turma_id')
            turma = get_object_or_404(Turma, id=turma_id)
            codigo = turma.codigo
            try:
                turma.delete()
                messages.success(request, f'Turma {codigo} excluída!')
            except Exception as e:
                messages.error(request, f'Não é possível excluir: {str(e)}')
        
        return redirect('admin_turmas')
    
    return render(request, 'escola/admin_turmas.html', {
        'turmas': turmas,
        'cursos': cursos,
        'turnos': Turma.TURNO_CHOICES,
    })


@login_required
def admin_cursos(request):
    if not check_admin_permission(request.user):
        return redirect('home')
    
    cursos = Curso.objects.annotate(
        total_turmas=Count('turma'),
        total_disciplinas=Count('disciplinas')
    ).order_by('nome')
    disciplinas = Disciplina.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_curso':
            nome = request.POST.get('nome')
            codigo = request.POST.get('codigo')
            carga_horaria = request.POST.get('carga_horaria')
            descricao = request.POST.get('descricao', '')
            
            if nome and codigo and carga_horaria:
                try:
                    Curso.objects.create(
                        nome=nome,
                        codigo=codigo,
                        carga_horaria=int(carga_horaria),
                        descricao=descricao
                    )
                    messages.success(request, f'Curso {nome} criado com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar curso: {str(e)}')
            else:
                messages.error(request, 'Preencha nome, código e carga horária.')
        
        elif action == 'edit_curso':
            curso_id = request.POST.get('curso_id')
            curso = get_object_or_404(Curso, id=curso_id)
            curso.nome = request.POST.get('nome', curso.nome)
            curso.codigo = request.POST.get('codigo', curso.codigo)
            carga_horaria = request.POST.get('carga_horaria')
            if carga_horaria:
                curso.carga_horaria = int(carga_horaria)
            curso.descricao = request.POST.get('descricao', curso.descricao)
            curso.save()
            messages.success(request, f'Curso {curso.nome} atualizado!')
        
        elif action == 'delete_curso':
            curso_id = request.POST.get('curso_id')
            curso = get_object_or_404(Curso, id=curso_id)
            nome = curso.nome
            try:
                curso.delete()
                messages.success(request, f'Curso {nome} excluído!')
            except Exception as e:
                messages.error(request, f'Não é possível excluir: {str(e)}')
        
        elif action == 'add_disciplina':
            nome = request.POST.get('nome')
            curso_id = request.POST.get('curso')
            ementa = request.POST.get('ementa', '')
            
            if nome and curso_id:
                try:
                    Disciplina.objects.create(
                        nome=nome,
                        curso_id=curso_id,
                        ementa=ementa
                    )
                    messages.success(request, f'Disciplina {nome} criada!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar disciplina: {str(e)}')
        
        elif action == 'delete_disciplina':
            disciplina_id = request.POST.get('disciplina_id')
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)
            nome = disciplina.nome
            try:
                disciplina.delete()
                messages.success(request, f'Disciplina {nome} excluída!')
            except Exception as e:
                messages.error(request, f'Não é possível excluir: {str(e)}')
        
        return redirect('admin_cursos')
    
    return render(request, 'escola/admin_cursos.html', {
        'cursos': cursos,
        'disciplinas': disciplinas,
    })


@login_required
def admin_avisos(request):
    if not check_admin_permission(request.user):
        return redirect('home')
    
    avisos = Aviso.objects.all().order_by('-data_criacao')
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            titulo = request.POST.get('titulo')
            conteudo = request.POST.get('conteudo')
            destinatario = request.POST.get('destinatario', 'todos')
            turma_id = request.POST.get('turma')
            
            aviso = Aviso.objects.create(
                titulo=titulo,
                conteudo=conteudo,
                destinatario=destinatario,
                autor=request.user,
                turma_id=turma_id if turma_id else None
            )
            messages.success(request, 'Aviso criado com sucesso!')
        
        elif action == 'delete':
            aviso_id = request.POST.get('aviso_id')
            aviso = get_object_or_404(Aviso, id=aviso_id)
            aviso.delete()
            messages.success(request, 'Aviso excluído!')
        
        return redirect('admin_avisos')
    
    return render(request, 'escola/admin_avisos.html', {
        'avisos': avisos,
        'turmas': turmas,
    })


@login_required
def admin_eventos(request):
    if not check_admin_permission(request.user):
        return redirect('home')
    
    eventos = Evento.objects.all().order_by('-data')
    turmas = Turma.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            titulo = request.POST.get('titulo')
            data = request.POST.get('data')
            tipo = request.POST.get('tipo')
            descricao = request.POST.get('descricao', '')
            turma_id = request.POST.get('turma')
            
            Evento.objects.create(
                titulo=titulo,
                data=data,
                tipo=tipo,
                descricao=descricao,
                turma_id=turma_id if turma_id else None
            )
            messages.success(request, 'Evento criado com sucesso!')
        
        elif action == 'delete':
            evento_id = request.POST.get('evento_id')
            evento = get_object_or_404(Evento, id=evento_id)
            evento.delete()
            messages.success(request, 'Evento excluído!')
        
        return redirect('admin_eventos')
    
    return render(request, 'escola/admin_eventos.html', {
        'eventos': eventos,
        'turmas': turmas,
        'tipos_evento': Evento.TIPO_CHOICES,
    })


@login_required
def admin_configuracoes(request):
    if not check_admin_permission(request.user):
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
        
        return redirect('admin_configuracoes')
    
    return render(request, 'escola/admin_configuracoes.html', {'user': user})
