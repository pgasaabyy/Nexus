# 🏛️ Nexus - Sistema de Gestão Escolar Inteligente

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)

> **Nexus** é uma plataforma integrada de gestão escolar desenvolvida para centralizar processos acadêmicos, administrativos e pedagógicos. O sistema elimina a fragmentação de dados, oferecendo dashboards intuitivos para Direção, Secretaria, Professores e Alunos.

---

## 🎯 Objetivo do Projeto
Resolver a problemática da desorganização escolar causada por sistemas descentralizados. O Nexus conecta o lançamento de notas, controle de frequência e matrícula em um único ambiente seguro e escalável, pronto para instituições de ensino de pequeno a grande porte.

---

## 🚀 Funcionalidades Principais

### 🎓 Gestão Acadêmica
* **Controle de Turmas e Cursos:** Cadastro completo de grades curriculares e alocação de professores.
* **Matrícula Digital:** Vínculo de alunos em turmas com histórico de status (Ativo, Trancado, Concluído).
* **Diário de Classe:** Lançamento de frequência e conteúdo programático.

### 📊 Dashboards e Relatórios
* **API RESTful Integrada:** Fornecimento de dados em JSON para construção de gráficos dinâmicos.
* **Boletins Automáticos:** Geração de boletins em PDF (via `reportlab`).
* **Exportação de Dados:** Relatórios administrativos em Excel (via `openpyxl` e `django-import-export`).

### 👥 Perfis de Acesso (RBAC)
* **Admin/Secretaria:** Acesso total para cadastros e relatórios.
* **Professor:** Acesso restrito às suas turmas para lançar notas/chamada.
* **Aluno:** Visualização de boletim, frequência e materiais.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Back-end** | Python + Django | Núcleo da aplicação e regras de negócio. |
| **API** | Django REST Framework | Comunicação de dados para dashboards. |
| **Banco de Dados** | MySQL | Armazenamento relacional robusto. |
| **Front-end** | HTML5, Bootstrap, JS | Interface responsiva (Web). |
| **Relatórios** | ReportLab & OpenPyXL | Geração de documentos PDF e planilhas. |

---

## 💻 Instalação e Configuração

Siga este guia para rodar o projeto localmente (para desenvolvimento ou demonstração).

### Pré-requisitos
* Python 3.10 ou superior instalado.
* MySQL Server (8.0) instalado e rodando.Com certeza\! Um `README.md` bem escrito é a "vitrine" do seu projeto. Se você pretende vender esse sistema ou apresentá-lo como TCC, o documento precisa passar profissionalismo, clareza e mostrar que o software é robusto.

Aqui está o código completo em **Markdown**. Você deve salvar esse conteúdo em um arquivo chamado `README.md` na raiz do seu projeto (ao lado do `manage.py`).

-----

````markdown
# 🏛️ Nexus - Sistema de Gestão Escolar Inteligente

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)

> **Nexus** é uma plataforma integrada de gestão escolar desenvolvida para centralizar processos acadêmicos, administrativos e pedagógicos. O sistema elimina a fragmentação de dados, oferecendo dashboards intuitivos para Direção, Secretaria, Professores e Alunos.

---

## 🎯 Objetivo do Projeto
Resolver a problemática da desorganização escolar causada por sistemas descentralizados. O Nexus conecta o lançamento de notas, controle de frequência e matrícula em um único ambiente seguro e escalável, pronto para instituições de ensino de pequeno a grande porte.

---

## 🚀 Funcionalidades Principais

### 🎓 Gestão Acadêmica
* **Controle de Turmas e Cursos:** Cadastro completo de grades curriculares e alocação de professores.
* **Matrícula Digital:** Vínculo de alunos em turmas com histórico de status (Ativo, Trancado, Concluído).
* **Diário de Classe:** Lançamento de frequência e conteúdo programático.

### 📊 Dashboards e Relatórios
* **API RESTful Integrada:** Fornecimento de dados em JSON para construção de gráficos dinâmicos.
* **Boletins Automáticos:** Geração de boletins em PDF (via `reportlab`).
* **Exportação de Dados:** Relatórios administrativos em Excel (via `openpyxl` e `django-import-export`).

### 👥 Perfis de Acesso (RBAC)
* **Admin/Secretaria:** Acesso total para cadastros e relatórios.
* **Professor:** Acesso restrito às suas turmas para lançar notas/chamada.
* **Aluno:** Visualização de boletim, frequência e materiais.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Back-end** | Python + Django | Núcleo da aplicação e regras de negócio. |
| **API** | Django REST Framework | Comunicação de dados para dashboards. |
| **Banco de Dados** | MySQL | Armazenamento relacional robusto. |
| **Front-end** | HTML5, Bootstrap, JS | Interface responsiva (Web). |
| **Relatórios** | ReportLab & OpenPyXL | Geração de documentos PDF e planilhas. |

---

## 💻 Instalação e Configuração

Siga este guia para rodar o projeto localmente (para desenvolvimento ou demonstração).

### Pré-requisitos
* Python 3.10 ou superior instalado.
* MySQL Server (8.0) instalado e rodando.
* Git (opcional, para clonar o repositório).

### 1. Clonar o Repositório
```bash
git clone [https://github.com/seu-usuario/sistema-nexus.git](https://github.com/seu-usuario/sistema-nexus.git)
cd sistema-nexus
````

### 2\. Configurar o Ambiente Virtual

Recomendamos usar um ambiente virtual para não conflitar com outras bibliotecas do seu PC.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3\. Instalar Dependências

```bash
pip install -r requirements.txt
```

> *Caso não tenha o arquivo requirements.txt, instale manualmente:*
> `pip install django mysqlclient djangorestframework django-crispy-forms django-filter reportlab openpyxl django-import-export`

### 4\. Configurar o Banco de Dados (MySQL)

Acesse seu cliente MySQL (Workbench ou Terminal) e crie o banco:

```sql
DROP DATABASE IF EXISTS nexus;
CREATE DATABASE nexus CHARACTER SET utf8mb4;
```

*Nota: Certifique-se de que a senha do banco no arquivo `nexus/settings.py` corresponde à sua senha local.*

### 5\. Executar Migrações

Isso criará as tabelas no banco de dados automaticamente.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6\. Criar Superusuário (Admin)

Para acessar o painel administrativo do sistema:

```bash
python manage.py createsuperuser
# Siga as instruções na tela (usuário, email, senha)
```

### 7\. Iniciar o Servidor

```bash
python manage.py runserver
```

O sistema estará acessível em: `http://127.0.0.1:8000/`

-----

## 📡 Documentação da API

O Nexus possui endpoints prontos para integração com Dashboards (Power BI, Chart.js, etc).

  * **Base URL:** `http://127.0.0.1:8000/api/`
  * **Endpoints Disponíveis:**
      * `GET /api/alunos/` - Lista todos os alunos matriculados.
      * `GET /api/notas/` - Retorna o histórico de notas lançadas.
      * `GET /api/turmas/` - Dados das turmas ativas.

-----

## 📂 Estrutura do Projeto

```
sistema_nexus/
├── escola/             # App principal (Models, Views, API)
│   ├── migrations/     # Histórico do banco de dados
│   ├── models.py       # Estrutura das tabelas (Aluno, Professor, etc)
│   ├── serializers.py  # Configuração da API
│   └── views.py        # Lógica do sistema
├── nexus/              # Configurações globais (settings.py)
├── static/             # Arquivos CSS, JS e Imagens
├── templates/          # Arquivos HTML
├── manage.py           # Executor de comandos Django
└── requirements.txt    # Lista de bibliotecas
```

-----

## 🤝 Contribuição e Venda

Este projeto foi desenvolvido como **Software Proprietário** com fins acadêmicos e comerciais.
Para adquirir uma licença de uso, customização para sua escola ou contribuir com o código, entre em contato.

**Desenvolvedor:** [Seu Nome Aqui]
**Contato:** [seu.email@exemplo.com]
**LinkedIn:** [Link para seu perfil]

-----

\<p align="center"\>
Desenvolvido com ❤️ para o Trabalho de Conclusão de Curso - Sistema de Gestão Escolar - SENAI Morvan Figueiredo
\</p\>