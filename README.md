# 🏛️ Nexus - Sistema de Gestão Escolar Inteligente

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=for-the-badge)

> **Nexus** é uma plataforma integrada de gestão escolar desenvolvida para centralizar processos acadêmicos, administrativos e pedagógicos. O sistema elimina a fragmentação de dados, oferecendo dashboards intuitivos para Direção, Secretaria, Professores e Alunos.

---

## 🎯 Objetivo do Projeto
Resolver a problemática da desorganização escolar causada por sistemas descentralizados. O Nexus conecta o lançamento de notas, controle de frequência e matrícula em um único ambiente seguro e escalável.

---

## 🚀 Funcionalidades Principais

### 🎓 Gestão Acadêmica
* **Controle de Turmas e Cursos:** Cadastro completo de grades curriculares e alocação de professores.
* **Matrícula Digital:** Vínculo de alunos em turmas com histórico de status (Ativo, Trancado, Concluído).
* **Diário de Classe:** Lançamento de frequência e conteúdo programático.

### 📊 Dashboards e Relatórios
* **API RESTful Integrada:** Fornecimento de dados em JSON para construção de gráficos dinâmicos.
* **Boletins Automáticos:** Geração de boletins em PDF.
* **Exportação de Dados:** Relatórios administrativos em Excel.

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
| **Front-end** | HTML5, Bootstrap | Interface responsiva (Web). |
| **Relatórios** | ReportLab & OpenPyXL | Geração de documentos PDF e planilhas. |

---

## 💻 Instalação e Configuração

Siga este guia para rodar o projeto localmente.

### Pré-requisitos
* Python 3.10 ou superior.
* MySQL Server (8.0) rodando.
* Git instalado.

### 1. Clonar o Repositório
```bash
git clone [https://github.com/pgasaabyy/Nexus.git](https://github.com/pgasaabyy/Nexus.git)
cd Nexus
2. Configurar o Ambiente Virtual
Bash

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Instalar Dependências
Bash

pip install -r requirements.txt
Caso não tenha o arquivo requirements, instale manualmente: pip install django mysqlclient djangorestframework django-crispy-forms django-filter reportlab openpyxl django-import-export

4. Configurar o Banco de Dados
Abra seu terminal MySQL ou Workbench e rode:

SQL

DROP DATABASE IF EXISTS nexus;
CREATE DATABASE nexus CHARACTER SET utf8mb4;
5. Configurar Conexão (Se necessário)
Verifique se a senha do banco no arquivo nexus/settings.py bate com a do seu computador.

6. Executar Migrações
Bash

python manage.py makemigrations
python manage.py migrate
7. Criar Admin e Rodar
Bash

python manage.py createsuperuser
python manage.py runserver
Acesse: http://127.0.0.1:8000/

📡 Documentação da API
O Nexus possui endpoints prontos para integração com Dashboards.

Base URL: /api/

Endpoints:

GET /api/alunos/ - Lista de alunos.

GET /api/notas/ - Histórico de notas.

GET /api/turmas/ - Turmas ativas.

📂 Estrutura do Projeto
Nexus/
├── escola/             # App principal (Models, Views, API)
│   ├── migrations/     # Histórico do banco
│   ├── models.py       # Tabelas do Banco de Dados
│   ├── serializers.py  # Configuração da API
│   └── views.py        # Lógica do sistema
├── nexus/              # Configurações globais (settings.py)
├── manage.py           # Executor de comandos Django
└── requirements.txt    # Lista de bibliotecas
🤝 Autores
Este projeto foi desenvolvido como Trabalho de Conclusão de Curso (TEMA 4).

<p align="center"> <b>SENAI Morvan Figueiredo - 2025 </b>


Desenvolvido com ❤️ </p>