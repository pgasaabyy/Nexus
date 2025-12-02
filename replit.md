# NEXUS - Sistema de Gestão Escolar

## Visão Geral
Sistema de gestão escolar completo desenvolvido em Django 5.2 com PostgreSQL. O sistema possui módulos para Alunos, Professores, Secretaria e Coordenação.

## Alterações Recentes
- **02/12/2025:** Implementação de CRUD completo para alunos (secretaria) e eventos (coordenação)
- Novo branding NEXUS com logo atualizado em todas as páginas
- Formulários de adicionar/editar/excluir alunos na secretaria
- Gerenciamento de eventos do calendário escolar com filtros por tipo
- Sistema de comunicados para envio de avisos às turmas
- Correções de permissões de acesso por função
- Migração para PostgreSQL, organização de rotas, criação de templates base padronizados
- Corrigido sistema de autenticação com redirecionamento por função
- Criado comando `criar_dados_teste` para popular o banco com dados de exemplo

## Arquitetura do Projeto

### Estrutura Principal
```
nexus/              # Configurações do projeto Django
escola/             # App principal com models, views, templates
  ├── management/   # Comandos de gerenciamento customizados
  ├── static/       # CSS, JS, imagens
  ├── templates/    # Templates HTML com herança
  └── urls.py       # Rotas organizadas por função
```

### Modelos de Dados
- Curso, Disciplina, Turma
- Professor, Aluno, Matrícula
- Nota, Frequência
- Aviso, Evento, HorarioAula, Documento

### Templates Base
- `base_aluno.html` - Layout para alunos
- `base_professor.html` - Layout para professores
- `base_secretaria.html` - Layout para secretaria
- `base_coordenacao.html` - Layout para coordenação

### Funcionalidades por Perfil

**Aluno:**
- Visualizar boletim e frequência
- Exportar boletim em PDF
- Ver calendário e horários
- Justificar faltas

**Professor:**
- Lançar notas e frequência
- Gerenciar materiais didáticos
- Enviar comunicados
- Ver calendário

**Secretaria:**
- CRUD completo de alunos (adicionar/editar/excluir)
- Gerenciar professores e turmas
- Emitir documentos
- Visualizar calendário acadêmico

**Coordenação:**
- Gerenciar eventos do calendário (adicionar/editar/excluir)
- Enviar comunicados às turmas
- Gerar relatórios
- Supervisionar turmas e alunos

### URLs Importantes
- `/` - Página inicial
- `/login/` - Login
- `/dashboard/secretaria/alunos/adicionar/` - Adicionar aluno
- `/dashboard/coordenacao/calendario/evento/adicionar/` - Adicionar evento
- `/dashboard/coordenacao/comunicados/` - Enviar comunicados

## Configuração do Ambiente

### Variáveis de Ambiente
- `DATABASE_URL` - URL de conexão PostgreSQL
- `SECRET_KEY` - Chave secreta do Django
- `DEBUG` - Modo de debug (True/False)

### Comandos Úteis
```bash
python manage.py migrate              # Aplicar migrações
python manage.py criar_dados_teste    # Criar dados de teste
python manage.py collectstatic        # Coletar arquivos estáticos
python manage.py createsuperuser      # Criar admin
```

## Credenciais de Teste
| Usuário | Senha | Função |
|---------|-------|--------|
| admin | admin123 | Administrador |
| secretaria | secre123 | Secretaria |
| coordenacao | coord123 | Coordenação |
| professor | prof123 | Professor |
| lucas.oliveira | aluno123 | Aluno |

## Servidor de Desenvolvimento
- Porta: 5000
- Comando: `bash run.sh`
- URL: http://0.0.0.0:5000

## Dependências Principais
- Django 5.2.8
- djangorestframework
- psycopg2-binary (PostgreSQL)
- reportlab (PDF)
- openpyxl (Excel)
