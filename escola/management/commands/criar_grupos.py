from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria grupos de usuários com permissões apropriadas'

    def handle(self, *args, **options):
        grupos_config = {
            'Secretaria': {
                'permissoes': [
                    'add_aluno', 'change_aluno', 'delete_aluno', 'view_aluno',
                    'add_professor', 'change_professor', 'delete_professor', 'view_professor',
                    'add_turma', 'change_turma', 'delete_turma', 'view_turma',
                    'add_curso', 'change_curso', 'delete_curso', 'view_curso',
                    'add_disciplina', 'change_disciplina', 'delete_disciplina', 'view_disciplina',
                    'add_matricula', 'change_matricula', 'delete_matricula', 'view_matricula',
                    'add_documento', 'change_documento', 'delete_documento', 'view_documento',
                    'add_evento', 'change_evento', 'delete_evento', 'view_evento',
                    'add_aviso', 'change_aviso', 'delete_aviso', 'view_aviso',
                    'view_nota', 'view_frequencia',
                    'add_sala', 'change_sala', 'delete_sala', 'view_sala',
                ]
            },
            'Coordenacao': {
                'permissoes': [
                    'view_aluno', 'change_aluno',
                    'view_professor', 'change_professor',
                    'view_turma', 'change_turma',
                    'view_curso',
                    'view_disciplina',
                    'view_matricula',
                    'add_evento', 'change_evento', 'delete_evento', 'view_evento',
                    'add_aviso', 'change_aviso', 'delete_aviso', 'view_aviso',
                    'view_nota', 'change_nota',
                    'view_frequencia',
                    'view_documento',
                ]
            },
            'Professor': {
                'permissoes': [
                    'view_aluno',
                    'view_turma',
                    'view_disciplina',
                    'add_nota', 'change_nota', 'view_nota',
                    'add_frequencia', 'change_frequencia', 'view_frequencia',
                    'add_material', 'change_material', 'delete_material', 'view_material',
                    'add_aviso', 'view_aviso',
                    'view_evento',
                ]
            },
            'Aluno': {
                'permissoes': [
                    'view_nota',
                    'view_frequencia',
                    'view_evento',
                    'view_aviso',
                    'view_material',
                    'view_horarioaula',
                ]
            },
        }

        for grupo_nome, config in grupos_config.items():
            grupo, created = Group.objects.get_or_create(name=grupo_nome)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{grupo_nome}" criado'))
            else:
                self.stdout.write(self.style.WARNING(f'Grupo "{grupo_nome}" já existe'))
            
            grupo.permissions.clear()
            
            for perm_codename in config['permissoes']:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    grupo.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  Permissão "{perm_codename}" não encontrada'))
            
            self.stdout.write(f'  {grupo.permissions.count()} permissões atribuídas')

        self.stdout.write(self.style.SUCCESS('\nGrupos criados com sucesso!'))
