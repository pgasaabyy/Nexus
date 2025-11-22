from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Aluno, Nota
from .serializers import AlunoSerializer, NotaSerializer

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer