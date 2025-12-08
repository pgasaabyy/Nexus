from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import date, timedelta
import random

from escola.models import (
    Curso, Disciplina, Turma, Professor, Aluno, Matricula, 
    Nota, Frequencia, Evento, HorarioAula, Aviso, Sala
)


class Command(BaseCommand):
    help = 'Cria dados completos de teste para o sistema'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de teste...\n')
        
        self.criar_salas()
        self.criar_cursos_disciplinas()
        self.criar_turmas()
        self.criar_professores()
        self.criar_alunos()
        self.criar_horarios()
        self.criar_eventos()
        self.criar_avisos()
        self.criar_notas_frequencia()
        self.criar_usuarios_sistema()
        
        self.stdout.write(self.style.SUCCESS('\nTodos os dados foram criados com sucesso!'))

    def criar_salas(self):
        salas_data = [
            {'nome': 'Sala 101', 'capacidade': 40, 'tipo': 'Sala de Aula', 'bloco': 'A'},
            {'nome': 'Sala 102', 'capacidade': 40, 'tipo': 'Sala de Aula', 'bloco': 'A'},
            {'nome': 'Sala 103', 'capacidade': 35, 'tipo': 'Sala de Aula', 'bloco': 'A'},
            {'nome': 'Lab Info 01', 'capacidade': 30, 'tipo': 'Laboratório', 'bloco': 'B'},
            {'nome': 'Lab Info 02', 'capacidade': 30, 'tipo': 'Laboratório', 'bloco': 'B'},
            {'nome': 'Auditório', 'capacidade': 100, 'tipo': 'Auditório', 'bloco': 'C'},
        ]
        
        for sala_data in salas_data:
            Sala.objects.get_or_create(nome=sala_data['nome'], defaults=sala_data)
        
        self.stdout.write(self.style.SUCCESS(f'  {len(salas_data)} salas criadas'))

    def criar_cursos_disciplinas(self):
        cursos_data = [
            {
                'nome': 'Técnico em Informática',
                'codigo': 'TEC-INF',
                'carga_horaria': 1200,
                'disciplinas': [
                    'Programação I', 'Programação II', 'Banco de Dados',
                    'Redes de Computadores', 'Sistemas Operacionais', 'Web Design'
                ]
            },
            {
                'nome': 'Técnico em Administração',
                'codigo': 'TEC-ADM',
                'carga_horaria': 1000,
                'disciplinas': [
                    'Contabilidade', 'Gestão de Pessoas', 'Marketing',
                    'Empreendedorismo', 'Gestão Financeira', 'Direito Empresarial'
                ]
            },
            {
                'nome': 'Técnico em Enfermagem',
                'codigo': 'TEC-ENF',
                'carga_horaria': 1800,
                'disciplinas': [
                    'Anatomia', 'Fisiologia', 'Farmacologia',
                    'Enfermagem Clínica', 'Primeiros Socorros', 'Saúde Coletiva'
                ]
            },
        ]

        for curso_data in cursos_data:
            curso, created = Curso.objects.get_or_create(
                codigo=curso_data['codigo'],
                defaults={
                    'nome': curso_data['nome'],
                    'carga_horaria': curso_data['carga_horaria']
                }
            )
            
            for disc_nome in curso_data['disciplinas']:
                Disciplina.objects.get_or_create(
                    nome=disc_nome,
                    curso=curso
                )
        
        self.stdout.write(self.style.SUCCESS(f'  {len(cursos_data)} cursos e disciplinas criados'))

    def criar_turmas(self):
        cursos = Curso.objects.all()
        turnos = ['Manhã', 'Tarde', 'Noite']
        
        count = 0
        for curso in cursos:
            for i, turno in enumerate(turnos[:2], 1):
                codigo = f"{curso.codigo[:3]}-{2024}-{i}"
                Turma.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'semestre': '2024/1',
                        'turno': turno,
                        'curso': curso
                    }
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  {count} turmas criadas'))

    def criar_professores(self):
        professores_data = [
            {'nome': 'Prof. Carlos Silva', 'email': 'carlos.silva@escola.com', 'especialidade': 'Programação'},
            {'nome': 'Prof. Ana Santos', 'email': 'ana.santos@escola.com', 'especialidade': 'Banco de Dados'},
            {'nome': 'Prof. Roberto Lima', 'email': 'roberto.lima@escola.com', 'especialidade': 'Redes'},
            {'nome': 'Prof. Maria Oliveira', 'email': 'maria.oliveira@escola.com', 'especialidade': 'Administração'},
            {'nome': 'Prof. João Pereira', 'email': 'joao.pereira@escola.com', 'especialidade': 'Saúde'},
        ]

        grupo_professor, _ = Group.objects.get_or_create(name='Professor')

        for prof_data in professores_data:
            professor, created = Professor.objects.get_or_create(
                email=prof_data['email'],
                defaults={
                    'nome': prof_data['nome'],
                    'especialidade': prof_data['especialidade'],
                    'data_admissao': date.today() - timedelta(days=random.randint(100, 1000))
                }
            )
            
            if created and not professor.user:
                username = prof_data['email'].split('@')[0].replace('.', '_')
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': prof_data['email'],
                        'first_name': prof_data['nome'].split()[-1],
                        'last_name': prof_data['nome'].split()[0].replace('Prof.', '').strip()
                    }
                )
                if user_created:
                    user.set_password('123456')
                    user.save()
                    user.groups.add(grupo_professor)
                professor.user = user
                professor.save()
        
        self.stdout.write(self.style.SUCCESS(f'  {len(professores_data)} professores criados'))

    def criar_alunos(self):
        nomes = [
            'Lucas Ferreira', 'Juliana Costa', 'Pedro Almeida', 'Camila Rodrigues',
            'Mateus Souza', 'Beatriz Lima', 'Gabriel Santos', 'Larissa Oliveira',
            'Thiago Martins', 'Amanda Carvalho', 'Rafael Nascimento', 'Fernanda Gomes',
            'Bruno Araújo', 'Isabela Silva', 'Felipe Ribeiro', 'Carolina Pereira',
            'Diego Barbosa', 'Mariana Dias', 'Henrique Moura', 'Letícia Freitas'
        ]

        turmas = list(Turma.objects.all())
        grupo_aluno, _ = Group.objects.get_or_create(name='Aluno')
        
        count = 0
        for i, nome in enumerate(nomes):
            matricula = f"2024{str(i+1).zfill(4)}"
            email = f"{nome.lower().replace(' ', '.')}@aluno.escola.com"
            cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            
            turma = turmas[i % len(turmas)] if turmas else None
            
            aluno, created = Aluno.objects.get_or_create(
                matricula=matricula,
                defaults={
                    'nome': nome,
                    'email': email,
                    'cpf': cpf,
                    'data_nascimento': date(2000 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                    'turma_atual': turma
                }
            )
            
            if created:
                count += 1
                if turma:
                    Matricula.objects.get_or_create(
                        aluno=aluno,
                        turma=turma,
                        defaults={'status': 'Ativo'}
                    )
                
                username = f"aluno{matricula}"
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': nome.split()[0],
                        'last_name': nome.split()[-1]
                    }
                )
                if user_created:
                    user.set_password('123456')
                    user.save()
                    user.groups.add(grupo_aluno)
                aluno.user = user
                aluno.save()
        
        self.stdout.write(self.style.SUCCESS(f'  {count} alunos criados'))

    def criar_horarios(self):
        turmas = Turma.objects.all()
        dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
        horarios_manha = [('07:00', '07:50'), ('07:50', '08:40'), ('08:40', '09:30'), ('09:50', '10:40'), ('10:40', '11:30')]
        horarios_tarde = [('13:00', '13:50'), ('13:50', '14:40'), ('14:40', '15:30'), ('15:50', '16:40'), ('16:40', '17:30')]
        
        count = 0
        for turma in turmas:
            disciplinas = list(turma.curso.disciplinas.all())
            horarios = horarios_manha if turma.turno == 'Manhã' else horarios_tarde
            
            for dia in dias:
                for i, (inicio, fim) in enumerate(horarios[:min(len(horarios), len(disciplinas))]):
                    disciplina = disciplinas[i % len(disciplinas)]
                    HorarioAula.objects.get_or_create(
                        turma=turma,
                        dia_semana=dia,
                        hora_inicio=inicio,
                        defaults={
                            'disciplina': disciplina,
                            'hora_fim': fim
                        }
                    )
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  {count} horários criados'))

    def criar_eventos(self):
        eventos_data = [
            {'titulo': 'Início do Semestre', 'tipo': 'evento', 'dias': 0},
            {'titulo': 'Feriado Nacional', 'tipo': 'feriado', 'dias': 15},
            {'titulo': 'Prova Bimestral', 'tipo': 'prova', 'dias': 30},
            {'titulo': 'Entrega de Trabalho', 'tipo': 'trabalho', 'dias': 45},
            {'titulo': 'Reunião de Pais', 'tipo': 'reuniao', 'dias': 60},
            {'titulo': 'Feira de Ciências', 'tipo': 'evento', 'dias': 75},
            {'titulo': 'Recesso Escolar', 'tipo': 'feriado', 'dias': 90},
        ]

        count = 0
        for evento_data in eventos_data:
            Evento.objects.get_or_create(
                titulo=evento_data['titulo'],
                defaults={
                    'data': date.today() + timedelta(days=evento_data['dias']),
                    'tipo': evento_data['tipo'],
                    'descricao': f"Evento: {evento_data['titulo']}"
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  {count} eventos criados'))

    def criar_avisos(self):
        avisos_data = [
            {'titulo': 'Bem-vindos ao Novo Semestre!', 'conteudo': 'Desejamos a todos um ótimo semestre letivo. Fiquem atentos aos comunicados.'},
            {'titulo': 'Calendário de Provas', 'conteudo': 'O calendário de provas bimestrais já está disponível. Consulte a coordenação.'},
            {'titulo': 'Biblioteca - Novos Horários', 'conteudo': 'A biblioteca funcionará em novo horário: 7h às 21h.'},
        ]

        admin = User.objects.filter(is_superuser=True).first()
        
        count = 0
        for aviso_data in avisos_data:
            Aviso.objects.get_or_create(
                titulo=aviso_data['titulo'],
                defaults={
                    'conteudo': aviso_data['conteudo'],
                    'autor': admin,
                    'destinatario': 'todos'
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  {count} avisos criados'))

    def criar_notas_frequencia(self):
        matriculas = Matricula.objects.all()
        
        count_notas = 0
        count_freq = 0
        
        for matricula in matriculas:
            disciplinas = matricula.turma.curso.disciplinas.all()
            
            for disciplina in disciplinas:
                for tipo in ['Prova 1', 'Prova 2', 'Trabalho']:
                    Nota.objects.get_or_create(
                        matricula=matricula,
                        disciplina=disciplina,
                        tipo_avaliacao=tipo,
                        defaults={
                            'valor': random.randint(50, 100) / 10,
                        }
                    )
                    count_notas += 1
                
                for i in range(10):
                    data = date.today() - timedelta(days=i*7)
                    Frequencia.objects.get_or_create(
                        matricula=matricula,
                        disciplina=disciplina,
                        data_aula=data,
                        defaults={
                            'presente': random.random() > 0.15
                        }
                    )
                    count_freq += 1
        
        self.stdout.write(self.style.SUCCESS(f'  {count_notas} notas e {count_freq} registros de frequência criados'))

    def criar_usuarios_sistema(self):
        grupo_secretaria, _ = Group.objects.get_or_create(name='Secretaria')
        grupo_coordenacao, _ = Group.objects.get_or_create(name='Coordenacao')

        usuarios_sistema = [
            {'username': 'secretaria', 'email': 'secretaria@escola.com', 'grupo': grupo_secretaria, 'nome': 'Secretaria'},
            {'username': 'coordenacao', 'email': 'coordenacao@escola.com', 'grupo': grupo_coordenacao, 'nome': 'Coordenação'},
        ]

        for user_data in usuarios_sistema:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['nome']
                }
            )
            if created:
                user.set_password('123456')
                user.save()
                user.groups.add(user_data['grupo'])
        
        if not User.objects.filter(is_superuser=True).exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@escola.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('  Superusuário admin criado (senha: admin123)'))
        
        self.stdout.write(self.style.SUCCESS('  Usuários do sistema criados'))
