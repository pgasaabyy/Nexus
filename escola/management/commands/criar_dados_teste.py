from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from escola.models import (
    Curso, Disciplina, Turma, Professor, Aluno, 
    Matricula, Nota, Frequencia, Aviso, Evento, HorarioAula
)
from datetime import date, time, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Cria dados de teste para o sistema NEXUS'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de teste...')
        
        # Criar grupos de permissão
        secretaria_group, _ = Group.objects.get_or_create(name='secretaria')
        coordenacao_group, _ = Group.objects.get_or_create(name='coordenacao')
        
        # Criar superusuário admin se não existir
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nexus.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superusuário admin criado (senha: admin123)'))
        
        # Criar usuário secretaria
        if not User.objects.filter(username='secretaria').exists():
            user_sec = User.objects.create_user('secretaria', 'secretaria@nexus.com', 'secre123')
            user_sec.first_name = 'Maria'
            user_sec.last_name = 'Secretária'
            user_sec.groups.add(secretaria_group)
            user_sec.save()
            self.stdout.write(self.style.SUCCESS('Usuário secretaria criado (senha: secre123)'))
        
        # Criar usuário coordenação
        if not User.objects.filter(username='coordenacao').exists():
            user_coord = User.objects.create_user('coordenacao', 'coordenacao@nexus.com', 'coord123')
            user_coord.first_name = 'João'
            user_coord.last_name = 'Coordenador'
            user_coord.groups.add(coordenacao_group)
            user_coord.save()
            self.stdout.write(self.style.SUCCESS('Usuário coordenacao criado (senha: coord123)'))
        
        # Criar curso
        curso, _ = Curso.objects.get_or_create(
            codigo='ENS-MEDIO',
            defaults={
                'nome': 'Ensino Médio',
                'descricao': 'Curso de Ensino Médio Regular',
                'carga_horaria': 3200
            }
        )
        
        # Criar disciplinas
        disciplinas_nomes = ['Matemática', 'Português', 'Biologia', 'Física', 'Química', 'História', 'Geografia', 'Inglês']
        disciplinas = []
        for nome in disciplinas_nomes:
            disc, _ = Disciplina.objects.get_or_create(
                nome=nome,
                curso=curso,
                defaults={'ementa': f'Ementa de {nome}'}
            )
            disciplinas.append(disc)
        
        # Criar turmas
        turmas = []
        for i, (codigo, semestre) in enumerate([('1A', '2025.1'), ('1B', '2025.1'), ('2A', '2025.1')]):
            turma, _ = Turma.objects.get_or_create(
                codigo=codigo,
                semestre=semestre,
                defaults={
                    'turno': ['Manhã', 'Tarde'][i % 2],
                    'curso': curso
                }
            )
            turmas.append(turma)
        
        # Criar professor com usuário
        if not User.objects.filter(username='professor').exists():
            user_prof = User.objects.create_user('professor', 'professor@nexus.com', 'prof123')
            user_prof.first_name = 'Carlos'
            user_prof.last_name = 'Professor'
            user_prof.save()
        else:
            user_prof = User.objects.get(username='professor')
        
        professor, created = Professor.objects.get_or_create(
            email='professor@nexus.com',
            defaults={
                'user': user_prof,
                'nome': 'Prof. Carlos Silva',
                'telefone': '(11) 99999-1234',
                'especialidade': 'Matemática',
                'data_admissao': date(2020, 3, 1)
            }
        )
        
        # Garantir vínculo do professor com o usuário
        if professor.user != user_prof:
            professor.user = user_prof
            professor.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('Usuário professor criado (senha: prof123)'))
        
        # Criar mais professores
        for i, nome in enumerate(['Ana Professora', 'Pedro Professor', 'Julia Professora']):
            Professor.objects.get_or_create(
                email=f'{nome.lower().replace(" ", "")}@nexus.com',
                defaults={
                    'nome': f'Prof. {nome}',
                    'telefone': f'(11) 9888{i}-1234',
                    'especialidade': disciplinas_nomes[i + 1] if i + 1 < len(disciplinas_nomes) else 'Geral',
                    'data_admissao': date(2021, i + 1, 15)
                }
            )
        
        # Criar alunos com usuários
        alunos_data = [
            ('Lucas Oliveira', '2024001', '111.222.333-44', turmas[0]),
            ('Maria Santos', '2024002', '222.333.444-55', turmas[0]),
            ('Pedro Costa', '2024003', '333.444.555-66', turmas[0]),
            ('Ana Silva', '2024004', '444.555.666-77', turmas[1]),
            ('João Pereira', '2024005', '555.666.777-88', turmas[1]),
            ('Carla Souza', '2024006', '666.777.888-99', turmas[2]),
        ]
        
        alunos = []
        for nome, matricula, cpf, turma in alunos_data:
            username = nome.lower().replace(' ', '.')
            if not User.objects.filter(username=username).exists():
                user_aluno = User.objects.create_user(username, f'{username}@nexus.com', 'aluno123')
                user_aluno.first_name = nome.split()[0]
                user_aluno.last_name = nome.split()[-1]
                user_aluno.save()
            else:
                user_aluno = User.objects.get(username=username)
            
            aluno, created = Aluno.objects.get_or_create(
                matricula=matricula,
                defaults={
                    'user': user_aluno,
                    'nome': nome,
                    'email': f'{username}@nexus.com',
                    'cpf': cpf,
                    'data_nascimento': date(2007, random.randint(1, 12), random.randint(1, 28)),
                    'telefone': f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                    'turma_atual': turma
                }
            )
            
            # Garantir vínculo do aluno com o usuário mesmo se já existia
            if aluno.user != user_aluno:
                aluno.user = user_aluno
                aluno.save()
            
            alunos.append(aluno)
            
            # Criar matrícula
            Matricula.objects.get_or_create(
                aluno=aluno,
                turma=turma,
                defaults={'status': 'Ativo'}
            )
        
        self.stdout.write(self.style.SUCCESS(f'{len(alunos)} alunos criados/atualizados (senha padrão: aluno123)'))
        
        # Criar notas para os alunos
        for aluno in alunos:
            matricula = Matricula.objects.filter(aluno=aluno).first()
            if matricula:
                for disc in disciplinas[:4]:  # Apenas 4 disciplinas para teste
                    if not Nota.objects.filter(matricula=matricula, disciplina=disc).exists():
                        for tipo in ['Prova 1', 'Prova 2']:
                            Nota.objects.create(
                                matricula=matricula,
                                disciplina=disc,
                                valor=Decimal(str(round(random.uniform(5.0, 10.0), 1))),
                                tipo_avaliacao=tipo,
                                data_lancamento=date.today() - timedelta(days=random.randint(1, 30))
                            )
        
        # Criar frequência
        for aluno in alunos:
            matricula = Matricula.objects.filter(aluno=aluno).first()
            if matricula:
                for disc in disciplinas[:4]:
                    for i in range(10):  # 10 aulas por disciplina
                        data_aula = date.today() - timedelta(days=i * 2)
                        Frequencia.objects.get_or_create(
                            matricula=matricula,
                            disciplina=disc,
                            data_aula=data_aula,
                            defaults={'presente': random.random() > 0.2}  # 80% presença
                        )
        
        # Criar avisos
        avisos_data = [
            ('Reunião de Pais', 'A reunião de pais será realizada no próximo sábado às 9h.'),
            ('Prova Bimestral', 'As provas bimestrais começam na próxima segunda-feira.'),
            ('Feira de Ciências', 'Inscrições abertas para a Feira de Ciências 2025.'),
        ]
        for titulo, conteudo in avisos_data:
            Aviso.objects.get_or_create(titulo=titulo, defaults={'conteudo': conteudo})
        
        # Criar eventos
        eventos_data = [
            ('Início das Aulas', date(2025, 2, 3), 'evento'),
            ('Carnaval', date(2025, 3, 3), 'feriado'),
            ('Prova de Matemática', date(2025, 3, 15), 'prova'),
            ('Entrega de Trabalho', date(2025, 3, 20), 'trabalho'),
        ]
        for titulo, data, tipo in eventos_data:
            Evento.objects.get_or_create(
                titulo=titulo,
                data=data,
                defaults={'tipo': tipo, 'descricao': f'Descrição do evento: {titulo}'}
            )
        
        # Criar horários de aula
        horarios_padrao = [
            (time(7, 0), time(7, 50)),
            (time(7, 50), time(8, 40)),
            (time(8, 40), time(9, 30)),
            (time(9, 50), time(10, 40)),
            (time(10, 40), time(11, 30)),
        ]
        dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
        
        for turma in turmas:
            for i, dia in enumerate(dias):
                for j, (inicio, fim) in enumerate(horarios_padrao[:3]):
                    disc_idx = (i + j) % len(disciplinas)
                    HorarioAula.objects.get_or_create(
                        turma=turma,
                        disciplina=disciplinas[disc_idx],
                        dia_semana=dia,
                        hora_inicio=inicio,
                        defaults={'hora_fim': fim}
                    )
        
        self.stdout.write(self.style.SUCCESS('Dados de teste criados com sucesso!'))
        self.stdout.write('')
        self.stdout.write('Credenciais de acesso:')
        self.stdout.write('- Admin: admin / admin123')
        self.stdout.write('- Secretaria: secretaria / secre123')
        self.stdout.write('- Coordenação: coordenacao / coord123')
        self.stdout.write('- Professor: professor / prof123')
        self.stdout.write('- Alunos: lucas.oliveira, maria.santos, etc. / aluno123')
