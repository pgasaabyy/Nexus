from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
# from .models import Aluno, Professor, Curso, Turma, Disciplina, Documento, Modelo, Matricula, Tarefa


@login_required
def dashboard(request):
    """Dashboard principal da secretaria"""
    context = {
        'total_alunos': 1284,  # Replace with: Aluno.objects.count()
        'total_professores': 87,  # Replace with: Professor.objects.filter(status='ativo').count()
        'total_turmas': 42,  # Replace with: Turma.objects.filter(ativa=True).count()
        'receita_mensal': 248500,  # Calculate from your model
        'variacao_receita': 8.2,  # Calculate percentage
        'matriculas_recentes': [],  # Replace with: Matricula.objects.order_by('-data_matricula')[:5]
        'tarefas_pendentes': [],  # Replace with: Tarefa.objects.filter(status='pendente')
    }
    return render(request, 'dashboard.html', context)


@login_required
def alunos_lista(request):
    """Lista de alunos com paginação"""
    # alunos_list = Aluno.objects.all().select_related('turma')
    alunos_list = []  # Replace with actual query
    
    paginator = Paginator(alunos_list, 20)  # 20 alunos por página
    page_number = request.GET.get('page')
    alunos = paginator.get_page(page_number)
    
    context = {'alunos': alunos}
    return render(request, 'alunos.html', context)


@login_required
def aluno_criar(request):
    """Criar novo aluno"""
    # Implement form logic here
    return render(request, 'aluno_form.html')


@login_required
def aluno_editar(request, pk):
    """Editar aluno existente"""
    # aluno = get_object_or_404(Aluno, pk=pk)
    # Implement form logic here
    return render(request, 'aluno_form.html')


@login_required
def aluno_detalhe(request, pk):
    """Detalhes do aluno"""
    # aluno = get_object_or_404(Aluno, pk=pk)
    return render(request, 'aluno_detalhe.html')


@login_required
def aluno_documentos(request, pk):
    """Documentos do aluno"""
    # aluno = get_object_or_404(Aluno, pk=pk)
    return render(request, 'aluno_documentos.html')


@login_required
def professores_lista(request):
    """Lista de professores com paginação"""
    # professores_list = Professor.objects.all().prefetch_related('disciplinas')
    professores_list = []  # Replace with actual query
    
    paginator = Paginator(professores_list, 20)
    page_number = request.GET.get('page')
    professores = paginator.get_page(page_number)
    
    context = {'professores': professores}
    return render(request, 'professores.html', context)


@login_required
def professor_criar(request):
    """Criar novo professor"""
    return render(request, 'professor_form.html')


@login_required
def professor_editar(request, pk):
    """Editar professor existente"""
    # professor = get_object_or_404(Professor, pk=pk)
    return render(request, 'professor_form.html')


@login_required
def professor_detalhe(request, pk):
    """Detalhes do professor"""
    # professor = get_object_or_404(Professor, pk=pk)
    return render(request, 'professor_detalhe.html')


@login_required
def professor_documentos(request, pk):
    """Documentos do professor"""
    # professor = get_object_or_404(Professor, pk=pk)
    return render(request, 'professor_documentos.html')


@login_required
def academico(request):
    """Gestão acadêmica - cursos, turmas e disciplinas"""
    context = {
        'cursos': [],  # Replace with: Curso.objects.all()
        'turmas': [],  # Replace with: Turma.objects.all()
        'disciplinas': [],  # Replace with: Disciplina.objects.all()
    }
    return render(request, 'academico.html', context)


@login_required
def curso_criar(request):
    """Criar novo curso"""
    return render(request, 'curso_form.html')


@login_required
def curso_editar(request, pk):
    """Editar curso existente"""
    # curso = get_object_or_404(Curso, pk=pk)
    return render(request, 'curso_form.html')


@login_required
def turma_editar(request, pk):
    """Editar turma existente"""
    # turma = get_object_or_404(Turma, pk=pk)
    return render(request, 'turma_form.html')


@login_required
def disciplina_editar(request, pk):
    """Editar disciplina existente"""
    # disciplina = get_object_or_404(Disciplina, pk=pk)
    return render(request, 'disciplina_form.html')


@login_required
def documentos_lista(request):
    """Lista de documentos e modelos"""
    context = {
        'documentos': [],  # Replace with: Documento.objects.all()
        'modelos': [],  # Replace with: Modelo.objects.all()
    }
    return render(request, 'documentos.html', context)


@login_required
def documento_download(request, pk):
    """Download de documento"""
    # documento = get_object_or_404(Documento, pk=pk)
    # return FileResponse(documento.arquivo.open(), as_attachment=True)
    raise Http404("Documento não encontrado")


@login_required
def documento_visualizar(request, pk):
    """Visualizar documento"""
    # documento = get_object_or_404(Documento, pk=pk)
    return render(request, 'documento_visualizar.html')


@login_required
def modelo_download(request, pk):
    """Download de modelo"""
    # modelo = get_object_or_404(Modelo, pk=pk)
    # return FileResponse(modelo.arquivo.open(), as_attachment=True)
    raise Http404("Modelo não encontrado")


@login_required
def modelo_visualizar(request, pk):
    """Visualizar modelo"""
    # modelo = get_object_or_404(Modelo, pk=pk)
    return render(request, 'modelo_visualizar.html')


@login_required
def calendario(request):
    """Calendário escolar"""
    return render(request, 'calendario.html')


@login_required
def configuracoes(request):
    """Configurações do sistema"""
    return render(request, 'configuracoes.html')


@login_required
def tarefas(request):
    """Lista de tarefas"""
    # tarefas = Tarefa.objects.filter(usuario=request.user)
    return render(request, 'tarefas.html')
