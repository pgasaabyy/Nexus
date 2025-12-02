from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from escola.models import Aluno, Professor, Turma, Curso, Matricula
from datetime import date


class Command(BaseCommand):
    help = 'Cria usuários de demonstração para todas as categorias do sistema'

    def handle(self, *args, **options):
        self.stdout.write('Criando grupos de permissão...')
        self.criar_grupos()
        
        self.stdout.write('Criando usuários de demonstração...')
        self.criar_usuarios()
        
        self.stdout.write(self.style.SUCCESS('Usuários e grupos criados com sucesso!'))
        self.stdout.write(self.style.WARNING('AVISO: Senhas padrão são apenas para demonstração!'))

    def criar_grupos(self):
        from escola.models import (
            Aluno, Professor, Turma, Curso, Disciplina, 
            Matricula, Nota, Frequencia, Aviso, Evento, 
            HorarioAula, Documento
        )
        
        admin_group, created = Group.objects.get_or_create(name='Admin')
        admin_group.permissions.clear()
        all_perms = Permission.objects.all()
        admin_group.permissions.add(*all_perms)
        if created:
            self.stdout.write(f'  - Grupo Admin criado com todas as permissões')
        else:
            self.stdout.write(f'  - Grupo Admin atualizado com todas as permissões')
        
        coordenacao, created = Group.objects.get_or_create(name='Coordenacao')
        coordenacao.permissions.clear()
        coordenacao_models = [
            Aluno, Professor, Turma, Curso, Disciplina,
            Matricula, Nota, Frequencia, Aviso, Evento,
            HorarioAula, Documento
        ]
        for model in coordenacao_models:
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            coordenacao.permissions.add(*perms)
        if created:
            self.stdout.write(f'  - Grupo Coordenacao criado com permissões completas')
        else:
            self.stdout.write(f'  - Grupo Coordenacao atualizado')
        
        secretaria, created = Group.objects.get_or_create(name='Secretaria')
        secretaria.permissions.clear()
        secretaria_full = [Aluno, Matricula, Documento, Turma]
        for model in secretaria_full:
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            secretaria.permissions.add(*perms)
        
        secretaria_view = [Professor, Curso, Disciplina, Evento, Aviso]
        for model in secretaria_view:
            ct = ContentType.objects.get_for_model(model)
            view_perm = Permission.objects.filter(content_type=ct, codename__startswith='view_')
            secretaria.permissions.add(*view_perm)
        if created:
            self.stdout.write(f'  - Grupo Secretaria criado com permissões administrativas')
        else:
            self.stdout.write(f'  - Grupo Secretaria atualizado')
        
        professor_group, created = Group.objects.get_or_create(name='Professor')
        professor_group.permissions.clear()
        professor_full = [Nota, Frequencia, Aviso]
        for model in professor_full:
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            professor_group.permissions.add(*perms)
        
        professor_view = [Aluno, Turma, Disciplina, Evento, HorarioAula, Matricula]
        for model in professor_view:
            ct = ContentType.objects.get_for_model(model)
            view_perm = Permission.objects.filter(content_type=ct, codename__startswith='view_')
            professor_group.permissions.add(*view_perm)
        if created:
            self.stdout.write(f'  - Grupo Professor criado com permissões de lançamento')
        else:
            self.stdout.write(f'  - Grupo Professor atualizado')
        
        aluno_group, created = Group.objects.get_or_create(name='Aluno')
        aluno_group.permissions.clear()
        aluno_view = [Nota, Frequencia, Aviso, Evento, HorarioAula, Turma, Disciplina]
        for model in aluno_view:
            ct = ContentType.objects.get_for_model(model)
            view_perm = Permission.objects.filter(content_type=ct, codename__startswith='view_')
            aluno_group.permissions.add(*view_perm)
        if created:
            self.stdout.write(f'  - Grupo Aluno criado com permissões de visualização')
        else:
            self.stdout.write(f'  - Grupo Aluno atualizado')

    def criar_usuarios(self):
        admin_group = Group.objects.get(name='Admin')
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@nexus.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Administrador',
                'last_name': 'Sistema'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        admin.groups.clear()
        admin.groups.add(admin_group)
        self.stdout.write(f'  - Admin: admin / admin123')
        
        coord_group = Group.objects.get(name='Coordenacao')
        coord_user, created = User.objects.get_or_create(
            username='coordenacao',
            defaults={
                'email': 'coordenacao@nexus.com',
                'is_staff': True,
                'first_name': 'Maria',
                'last_name': 'Coordenadora'
            }
        )
        if created:
            coord_user.set_password('coord123')
            coord_user.save()
        coord_user.groups.clear()
        coord_user.groups.add(coord_group)
        self.stdout.write(f'  - Coordenação: coordenacao / coord123')
        
        secre_group = Group.objects.get(name='Secretaria')
        secre_user, created = User.objects.get_or_create(
            username='secretaria',
            defaults={
                'email': 'secretaria@nexus.com',
                'is_staff': True,
                'first_name': 'Ana',
                'last_name': 'Secretária'
            }
        )
        if created:
            secre_user.set_password('secre123')
            secre_user.save()
        secre_user.groups.clear()
        secre_user.groups.add(secre_group)
        self.stdout.write(f'  - Secretaria: secretaria / secre123')
        
        prof_group = Group.objects.get(name='Professor')
        prof_user, created = User.objects.get_or_create(
            username='professor',
            defaults={
                'email': 'professor@nexus.com',
                'is_staff': False,
                'first_name': 'Carlos',
                'last_name': 'Professor'
            }
        )
        if created:
            prof_user.set_password('prof123')
            prof_user.save()
        prof_user.groups.clear()
        prof_user.groups.add(prof_group)
        
        professor_obj, _ = Professor.objects.get_or_create(
            email='professor@nexus.com',
            defaults={
                'user': prof_user,
                'nome': 'Carlos Professor',
                'telefone': '(11) 98765-4321',
                'especialidade': 'Matemática',
                'data_admissao': date(2020, 3, 1)
            }
        )
        if not professor_obj.user:
            professor_obj.user = prof_user
            professor_obj.save()
        self.stdout.write(f'  - Professor: professor / prof123')
        
        aluno_group = Group.objects.get(name='Aluno')
        aluno_user, created = User.objects.get_or_create(
            username='aluno',
            defaults={
                'email': 'aluno@nexus.com',
                'is_staff': False,
                'first_name': 'João',
                'last_name': 'Aluno'
            }
        )
        if created:
            aluno_user.set_password('aluno123')
            aluno_user.save()
        aluno_user.groups.clear()
        aluno_user.groups.add(aluno_group)
        
        curso, _ = Curso.objects.get_or_create(
            codigo='EM001',
            defaults={
                'nome': 'Ensino Médio',
                'descricao': 'Curso de Ensino Médio',
                'carga_horaria': 3200
            }
        )
        
        turma, _ = Turma.objects.get_or_create(
            codigo='1A-2024',
            defaults={
                'semestre': '2024.1',
                'turno': 'Manhã',
                'curso': curso
            }
        )
        
        aluno_obj, _ = Aluno.objects.get_or_create(
            email='aluno@nexus.com',
            defaults={
                'user': aluno_user,
                'matricula': '2024001',
                'nome': 'João Aluno Silva',
                'cpf': '123.456.789-00',
                'data_nascimento': date(2005, 5, 15),
                'telefone': '(11) 91234-5678',
                'turma_atual': turma
            }
        )
        if not aluno_obj.user:
            aluno_obj.user = aluno_user
            aluno_obj.save()
        
        Matricula.objects.get_or_create(
            aluno=aluno_obj,
            turma=turma,
            defaults={'status': 'Ativo'}
        )
        self.stdout.write(f'  - Aluno: aluno / aluno123')
        
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=== CREDENCIAIS DE ACESSO (DEMO) ==='))
        self.stdout.write(self.style.SUCCESS('Admin: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Coordenação: coordenacao / coord123'))
        self.stdout.write(self.style.SUCCESS('Secretaria: secretaria / secre123'))
        self.stdout.write(self.style.SUCCESS('Professor: professor / prof123'))
        self.stdout.write(self.style.SUCCESS('Aluno: aluno / aluno123'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Hierarquia de permissões:'))
        self.stdout.write('  Admin > Coordenação > Secretaria > Professor > Aluno')
