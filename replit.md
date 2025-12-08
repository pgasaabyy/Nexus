# NEXUS - Sistema de Gestão Escolar

## Visão Geral
Sistema de gestão escolar completo desenvolvido em Django 5.2 com PostgreSQL. O sistema possui módulos para Alunos, Professores, Secretaria e Coordenação, com design responsivo e funcionalidades CRUD completas.

## Alterações Recentes
- **08/12/2025:** CRUD completo para Coordenação gerenciar Turmas e Alunos
  - Novas views: coordenacao_turma_adicionar, coordenacao_turma_editar, coordenacao_turma_excluir
  - Novas views: coordenacao_aluno_adicionar, coordenacao_aluno_editar, coordenacao_aluno_excluir
  - Templates: coor_turma_form.html, coor_aluno_form.html, coor_turma_excluir.html, coor_aluno_excluir.html
  - Correção de parsing de data_nascimento usando datetime.strptime
  - Padronização de logos em todos os templates base (usando imagem logo-nexus.png)
  - Redesign de aluno_calendario.html com layout moderno
  - Gráfico de frequência do aluno agora usa dados reais (porcentagem_geral)
  - Página de relatórios (coor_relatorios.html) com analytics detalhados e exportação

- **08/12/2025:** Atualização completa de views e templates
  - Adicionada funcionalidade de configurações para todos os perfis (aluno, professor, secretaria, coordenação)
  - Views de configurações agora permitem atualizar perfil e alterar senha
  - Templates de professor (materiais, comunicados, calendário, configurações) convertidos para usar base_professor.html
  - Adicionada view de download de materiais
  - Criação automática de migrações e grupos no run.sh
  - Modelo Material com suporte a upload de arquivos
  - Modelo Sala para gerenciamento de salas de aula
  - Campo 'ativo', 'autor' e 'destinatario' adicionados ao modelo Aviso
  - Grupos criados automaticamente: Secretaria (42 perms), Coordenação (21 perms), Professor (16 perms), Aluno (6 perms)
  - CSS responsivo com breakpoints para tablet e mobile

- **02/12/2025:** Refatoração completa dos templates para usar herança de base templates
- **02/12/2025:** Implementação de CRUD completo para alunos (secretaria) e eventos (coordenação)

## Padrão de Design CSS
- Cor primária NEXUS: #092F76 (azul escuro)
- Cor secundária: #8ED6D7 (pool blue)
- Cor de destaque: #B1B7DC (light blue)
- Cor de fundo: #EDEED9 (beige)
- Cartões com border-radius: 15px e box-shadow: 0 4px 15px rgba(0,0,0,0.08)
- Fonte: Poppins (Google Fonts)
- Botões com border-radius: 10px e transições suaves

## Arquitetura do Projeto

### Estrutura Principal
```
nexus/              # Configurações do projeto Django
escola/             # App principal com models, views, templates
  ├── management/   # Comandos de gerenciamento customizados
  │   └── commands/
  │       ├── criar_grupos.py        # Cria grupos e permissões hierárquicas
  │       └── criar_dados_completos.py # Popula banco com dados de teste
  ├── static/       # CSS, JS, imagens
  ├── templates/    # Templates HTML com herança
  └── urls.py       # Rotas organizadas por função
```

### Modelos de Dados
- Curso, Disciplina, Turma, Sala
- Professor, Aluno, Matrícula
- Nota, Frequência
- Aviso (com autor, destinatario, ativo), Evento, HorarioAula, Documento
- Material (novo - para upload de materiais didáticos)

### Templates Base
- `base_aluno.html` - Layout para alunos
- `base_professor.html` - Layout para professores (atualizado com SVG icons)
- `base_secretaria.html` - Layout para secretaria
- `base_coordenacao.html` - Layout para coordenação

### Funcionalidades por Perfil

**Aluno:**
- Visualizar boletim e frequência
- Exportar boletim em PDF
- Ver calendário e horários
- Justificar faltas
- Configurações de perfil e senha

**Professor:**
- Lançar notas e frequência
- Gerenciar materiais didáticos (upload/download/excluir)
- Enviar comunicados para turmas
- Gerenciar eventos do calendário
- Configurações de perfil e senha

**Secretaria:**
- CRUD completo de alunos (adicionar/editar/excluir)
- Gerenciar professores e turmas
- Emitir documentos
- Visualizar calendário acadêmico
- Configurações de perfil e senha

**Coordenação:**
- CRUD completo de turmas (adicionar/editar/excluir)
- CRUD completo de alunos (adicionar/editar/excluir)
- Gerenciar eventos do calendário (adicionar/editar/excluir)
- Enviar comunicados às turmas (com CRUD completo)
- Gerar relatórios com analytics detalhados
- Supervisionar professores
- Configurações de perfil e senha

### URLs Importantes
- `/` - Página inicial
- `/login/` - Login
- `/logout/` - Logout (redireciona para home)
- `/dashboard/professor/materiais/` - Gerenciar materiais
- `/dashboard/professor/materiais/download/<id>/` - Download de material
- `/dashboard/secretaria/alunos/adicionar/` - Adicionar aluno
- `/dashboard/coordenacao/turmas/` - Listar turmas
- `/dashboard/coordenacao/turmas/adicionar/` - Adicionar turma
- `/dashboard/coordenacao/turmas/editar/<id>/` - Editar turma
- `/dashboard/coordenacao/alunos/` - Listar alunos
- `/dashboard/coordenacao/alunos/adicionar/` - Adicionar aluno
- `/dashboard/coordenacao/alunos/editar/<id>/` - Editar aluno
- `/dashboard/coordenacao/calendario/evento/adicionar/` - Adicionar evento
- `/dashboard/coordenacao/comunicados/` - Enviar comunicados
- `/dashboard/coordenacao/relatorios/` - Relatórios com analytics

## Configuração do Ambiente

### Variáveis de Ambiente
- `DATABASE_URL` - URL de conexão PostgreSQL (automático no Replit)
- `SECRET_KEY` - Chave secreta do Django
- `DEBUG` - Modo de debug (True/False)

### Comandos Úteis
```bash
bash run.sh                           # Inicia servidor (inclui migrations e grupos)
python3.11 manage.py migrate          # Aplicar migrações
python3.11 manage.py criar_grupos     # Criar grupos e permissões
python3.11 manage.py criar_dados_completos # Criar dados de teste completos
python3.11 manage.py collectstatic    # Coletar arquivos estáticos
python3.11 manage.py createsuperuser  # Criar admin
```

## Hierarquia de Permissões
```
Admin > Coordenação > Secretaria > Professor > Aluno
```

Grupos são criados automaticamente pelo comando `criar_grupos`:
- **Secretaria**: 42 permissões (gestão completa de alunos, professores, documentos)
- **Coordenação**: 21 permissões (eventos, comunicados, relatórios)
- **Professor**: 16 permissões (notas, frequência, materiais)
- **Aluno**: 6 permissões (visualização)

## Credenciais de Teste
| Usuário | Senha | Função | Grupo |
|---------|-------|--------|-------|
| admin | admin123 | Administrador | Admin |
| coordenacao | coord123 | Coordenação | Coordenacao |
| secretaria | secre123 | Secretaria | Secretaria |
| professor | prof123 | Professor | Professor |
| aluno | aluno123 | Aluno | Aluno |

## Servidor de Desenvolvimento
- Porta: 5000
- Comando: `bash run.sh`
- URL: http://0.0.0.0:5000
- Python: 3.11

## Dependências Principais
- Django 5.2.8
- djangorestframework
- psycopg2-binary (PostgreSQL)
- reportlab (PDF)
- openpyxl (Excel)
- django-filter
- django-crispy-forms
- django-import-export
- gunicorn (produção)
- whitenoise (arquivos estáticos)

## Preferências do Usuário
- Sistema deve funcionar responsivamente em todos dispositivos (desktop, tablet, mobile)
- Design seguindo a paleta de cores NEXUS
- Gráficos e charts devem ser funcionais em todos dashboards
- Grupos devem ser criados automaticamente com permissões hierárquicas
