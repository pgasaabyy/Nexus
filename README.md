<div align="center">

  <img src="LINK_DA_SUA_LOGO_AQUI.png" alt="Nexus Logo" width="250">

  <h1>🏛️ Nexus - Sistema de Gestão Escolar Inteligente</h1>

  <p>
    <b>Centralização. Eficiência. Inovação.</b><br>
    O futuro da gestão acadêmica no SENAI Morvan Figueiredo.
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
    <img src="https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
    <img src="https://img.shields.io/badge/Status-Em_Desenvolvimento-F7DF1E?style=for-the-badge&logo=insomnia&logoColor=black" alt="Status">
  </p>

</div>

---

## 🎯 Objetivo do Projeto

> **O Problema:** Instituições de ensino sofrem com a fragmentação de dados, utilizando sistemas separados para notas, matrículas e frequência, gerando retrabalho e inconsistência.

> **A Solução Nexus:** Uma plataforma integrada que conecta **Direção, Secretaria, Professores e Alunos** em um único ecossistema seguro e escalável.

---

## 🚀 Funcionalidades & Módulos

### 🎓 Gestão Acadêmica

- ✅ **Controle de Turmas:** Alocação inteligente de professores e grades curriculares.
- ✅ **Matrícula Digital:** Vínculo de alunos com status (Ativo, Trancado, Concluído).
- ✅ **Diário de Classe:** Lançamento rápido de frequência e conteúdo.

### 📊 Dashboards e Intelligence

- 📈 **API RESTful:** Dados em tempo real para criação de gráficos dinâmicos.
- 📄 **Boletins PDF:** Geração automática de documentos oficiais.
- 📑 **Exportação Excel:** Relatórios administrativos completos.

### 👥 Segurança e Acesso (RBAC)

| Perfil             | Permissões Principais                                       |
|--------------------|-------------------------------------------------------------|
| **Admin/Secretaria** | Acesso total, cadastros, matrículas e relatórios gerenciais. |
| **Professor**        | Gestão de suas turmas, lançamento de notas e chamadas.      |
| **Aluno**            | Visualização de boletim, faltas e materiais de aula.        |

---


## 💻 Guia de Instalação Rápida

Prepare seu ambiente de desenvolvimento em **3 minutos**.

### 1. Pré-requisitos

- Python 3.10+
- MySQL Server 8.0+
- Git

### 2. Clonar e Configurar

```bash
# 1. Clone o repositório
git clone https://github.com/pgasaabyy/Nexus.git
cd Nexus

# 2. Crie o Ambiente Virtual
python -m venv venv

# 3. Ative o Ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instale as Dependências
pip install -r requirements.txt
````

### 3. Banco de Dados e Execução

Abra seu MySQL e execute o comando SQL abaixo:

```sql
CREATE DATABASE nexus CHARACTER SET utf8mb4;
```

Em seguida, volte ao terminal:

```bash
# Migre a estrutura para o banco
python manage.py makemigrations
python manage.py migrate

# Crie o usuário administrador
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver
```

🚀 Acesse: `http://127.0.0.1:8000/`

---

## 📡 API Endpoints

O Nexus é **API First**. Integre com PowerBI ou front-ends modernos.

```http
GET /api/alunos/  # Listagem completa de discentes
GET /api/notas/   # Histórico acadêmico
GET /api/turmas/  # Grades ativas
```

---

## 🤝 Time de Desenvolvimento

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/pgasaabyy">
        <img src="https://avatars.githubusercontent.com/u/178240823?v=4" width="100px;" alt="Foto pgasaabyy"/>
        <br />
        <sub><b>pgasaabyy</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/juliamodena15">
        <img src="https://avatars.githubusercontent.com/u/183606987?v=4" width="100px;" alt="Foto Julia"/>
        <br />
        <sub><b>Julia Modena</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/larissasalmeida6-hub">
        <img src="https://avatars.githubusercontent.com/u/235154108?v=4" width="100px;" alt="Foto Larissa"/>
        <br />
        <sub><b>Larissa Almeida</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/MaviSz01">
        <img src="https://avatars.githubusercontent.com/u/176519382?v=4" width="100px;" alt="Foto MaviSz01"/>
        <br />
        <sub><b>MaviSz01</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Natan-Sant">
        <img src="https://avatars.githubusercontent.com/u/177337038?v=4" width="100px;" alt="Foto Natan"/>
        <br />
        <sub><b>Natan Sant'anna</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/wellxsz">
        <img src="https://avatars.githubusercontent.com/u/177960375?v=4" width="100px;" alt="Foto Well"/>
        <br />
        <sub><b>wellxsz</b></sub>
      </a>
    </td>
  </tr>
</table>

---

<div align="center">
  <p>
    Desenvolvido com 💙 para o <b>Trabalho de Conclusão de Curso - Sistema de Gestão Escolar</b><br>
    SENAI Morvan Figueiredo - 2025
  </p>
</div>

