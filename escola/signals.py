from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='escola.Aluno')
def criar_matricula_para_aluno(sender, instance, created, **kwargs):
    from .models import Matricula
    
    if instance.turma_atual:
        matricula_existente = Matricula.objects.filter(
            aluno=instance,
            turma=instance.turma_atual
        ).exists()
        
        if not matricula_existente:
            Matricula.objects.create(
                aluno=instance,
                turma=instance.turma_atual,
                data_matricula=timezone.now().date(),
                status='Ativo'
            )
