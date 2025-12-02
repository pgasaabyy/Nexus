<div align="center">

  <img src="escola/static/escola/img/icon-nexus.png" alt="Nexus Logo" width="100">

  <h1>NEXUS - Sistema de Gestão Escolar</h1>

  <p>
    <b>Centralização. Eficiência. Inovação.</b><br>
    Sistema completo de gestão escolar desenvolvido em Django.
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </p>

</div>

---

## Funcionalidades

### Aluno
- Dashboard com visão geral de notas e frequência
- Visualização de boletim escolar
- Consulta de frequência por disciplina
- Grade de horários
- Calendário de eventos
- Exportação de boletim em PDF
- Exportação de frequência em PDF e Excel

### Professor
- Dashboard com turmas e avisos
- Lançamento de notas por turma/disciplina
- Registro de frequência/chamada
- Visualização de comunicados
- Calendário de eventos

### Secretaria
- Dashboard com estatísticas gerais
- Gestão de alunos (cadastro, busca, filtros)
- Gestão de professores
- Gestão acadêmica (cursos, turmas, disciplinas)
- Emissão de documentos
- Calendário institucional

### Coordenação
- Dashboard com indicadores
- Gestão de turmas
- Acompanhamento de alunos e professores
- Relatórios gerenciais
- Gestão de comunicados
- Calendário pedagógico

---

## Tecnologias

- **Backend:** Django 5.2
- **Banco de Dados:** PostgreSQL
- **Frontend:** HTML5, CSS3, JavaScript
- **API:** Django REST Framework
- **Relatórios:** ReportLab (PDF), OpenPyXL (Excel)

---

## Instalação

### Requisitos
- Python 3.11+
- PostgreSQL

### Passos

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd nexus
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
export DATABASE_URL="postgresql://usuario:senha@host:porta/banco"
export SECRET_KEY="sua-chave-secreta"
```

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Crie dados de teste (opcional):
```bash
python manage.py criar_dados_teste
```

6. Inicie o servidor:
```bash
python manage.py runserver 0.0.0.0:5000
```

---

## Credenciais de Teste

Após executar `criar_dados_teste`:

| Usuário | Senha | Função |
|---------|-------|--------|
| admin | admin123 | Administrador |
| secretaria | secre123 | Secretaria |
| coordenacao | coord123 | Coordenação |
| professor | prof123 | Professor |
| lucas.oliveira | aluno123 | Aluno |
| maria.santos | aluno123 | Aluno |

---

## Estrutura do Projeto

```
nexus/
├── escola/                 # App principal
│   ├── management/        # Comandos de gerenciamento
│   ├── migrations/        # Migrações do banco
│   ├── static/escola/     # Arquivos estáticos
│   │   ├── css/          # Estilos
│   │   ├── js/           # Scripts
│   │   └── img/          # Imagens
│   ├── templates/escola/  # Templates HTML
│   ├── admin.py          # Configuração do admin
│   ├── models.py         # Modelos de dados
│   ├── serializers.py    # Serializers da API
│   ├── urls.py           # Rotas da app
│   └── views.py          # Views/Controllers
├── nexus/                 # Configurações do projeto
│   ├── settings.py       # Configurações
│   ├── urls.py           # Rotas principais
│   └── wsgi.py           # Configuração WSGI
├── manage.py             # CLI do Django
├── requirements.txt      # Dependências
└── run.sh               # Script de inicialização
```

---

## Modelos de Dados

### Principais Entidades

- **Curso:** Cursos oferecidos pela instituição
- **Disciplina:** Disciplinas de cada curso
- **Turma:** Turmas com código, semestre e turno
- **Professor:** Professores com especialidade e vínculo
- **Aluno:** Alunos com matrícula e dados pessoais
- **Matrícula:** Vínculo aluno-turma com status
- **Nota:** Notas por disciplina e tipo de avaliação
- **Frequência:** Registro de presença por aula
- **Aviso:** Comunicados para turmas
- **Evento:** Eventos do calendário escolar
- **HorarioAula:** Grade de horários por turma
- **Documento:** Documentos emitidos

---

## API REST

Endpoints disponíveis:

```http
GET /api/alunos/      # Listagem de alunos
POST /api/alunos/     # Criar aluno
GET /api/notas/       # Listagem de notas
POST /api/notas/      # Criar nota
```

---

## Segurança

- Autenticação baseada em sessão do Django
- Controle de acesso por grupos de permissão
- Proteção CSRF em todos os formulários
- Validação de permissões por view

---

## Desenvolvimento

### Executar migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### Coletar arquivos estáticos
```bash
python manage.py collectstatic
```

### Criar superusuário
```bash
python manage.py createsuperuser
```

---

## Time de Desenvolvimento

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/pgasaabyy">
        <img src="https://avatars.githubusercontent.com/u/178240823?v=4" width="80px;" alt="pgasaabyy"/>
        <br /><sub><b>pgasaabyy</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/juliamodena15">
        <img src="https://avatars.githubusercontent.com/u/183606987?v=4" width="80px;" alt="Julia"/>
        <br /><sub><b>Julia Modena</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/larissasalmeida6-hub">
        <img src="https://avatars.githubusercontent.com/u/235154108?v=4" width="80px;" alt="Larissa"/>
        <br /><sub><b>Larissa Almeida</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/MaviSz01">
        <img src="https://avatars.githubusercontent.com/u/176519382?v=4" width="80px;" alt="MaviSz01"/>
        <br /><sub><b>MaviSz01</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Natan-Sant">
        <img src="https://avatars.githubusercontent.com/u/177337038?v=4" width="80px;" alt="Natan"/>
        <br /><sub><b>Natan Sant'anna</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/wellxsz">
        <img src="https://avatars.githubusercontent.com/u/177960375?v=4" width="80px;" alt="Well"/>
        <br /><sub><b>wellxsz</b></sub>
      </a>
    </td>
  </tr>
</table>

---

<div align="center">
  <p>
    Desenvolvido para o <b>Trabalho de Conclusão de Curso - Sistema de Gestão Escolar</b><br>
    SENAI Morvan Figueiredo - 2025
  </p>
</div>
