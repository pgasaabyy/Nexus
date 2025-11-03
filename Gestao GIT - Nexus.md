📘 Guia de Colaboração — Projeto Nexus
Colaboração eficiente com Git e GitHub

🧩 1. Instalação do Git
Antes de começar, instale o Git no seu computador:

Acesse: https://git-scm.com/downloads
Baixe a versão compatível com seu sistema operacional (Windows, macOS ou Linux).
Durante a instalação, mantenha todas as opções padrão (basta clicar em “Next” ou “Avançar” até concluir).
✅ Confirmação da instalação
Abra o terminal (Prompt de Comando, Terminal ou PowerShell) e execute:

bash


1
git --version
Se retornar algo como git version 2.xx.x, a instalação foi bem-sucedida! ✅

🧠 2. Clonando o repositório
Acesse o repositório Nexus no GitHub.
Clique em Code → HTTPS e copie o link (ex: https://github.com/seu-usuario/nexus.git).
Escolha uma pasta no seu computador para salvar o projeto (ex: Documentos/projetos/).
Abra o terminal nessa pasta e execute:
bash


1
git clone https://github.com/seu-usuario/nexus.git
Substitua seu-usuario pelo nome real do repositório. 

Após o clone, entre na pasta do projeto:
bash


1
cd nexus
🌿 3. Trabalhando na sua branch
Cada integrante tem sua própria branch, seguindo o padrão:
br-nome (ex: br-lari, br-saaby, br-natan).

Garanta que sua branch local está atualizada:
bash


1
2
git fetch
git checkout br-seu-nome
Se for a primeira vez, sua branch pode não existir localmente — mas, após o git fetch, ela estará disponível.

💡 Substitua seu-nome pelo seu nome de acordo com a tabela no final do guia. 

✏️ 4. Fazendo alterações
Edite, crie ou teste arquivos livremente na sua branch.

Quando concluir uma funcionalidade ou ajuste, registre suas alterações:

bash


1
2
3
git add .
git commit -m "SeuNome: descrição clara do que foi feito"
git push origin br-seu-nome
⚠️ Regra obrigatória:
Todos os commits devem começar com seu nome (exatamente como na branch) para facilitar o rastreamento.

✅ Exemplos válidos:

"Lari: criação da página de login"
"Natan: ajustes no CSS do dashboard"
"Mavi: implementação da validação de formulário"
❌ Evite:

"fix", "update", "fiz algo" — seja específico!
🔄 5. Enviando para o GitHub
Após o commit, envie suas alterações:

bash


1
git push origin br-seu-nome
Isso atualiza sua branch no GitHub, sem afetar o código principal (main).

💬 6. Compartilhando com o grupo (Pull Request)
Quando quiser integrar suas alterações ao projeto principal:

Acesse o repositório no GitHub.
Clique em Pull Requests → New Pull Request.
Em “compare”, selecione:
base: main
compare: br-seu-nome
Escreva uma descrição clara do que foi feito, incluindo:
Objetivo da mudança
Arquivos alterados
Testes realizados (se aplicável)
Clique em Create Pull Request.
📌 Um líder do projeto revisará seu código e fará o merge na main após aprovação. 

🔁 7. Mantendo seu projeto atualizado
Se outros integrantes atualizaram a main, sincronize seu ambiente:

bash


1
2
3
4
git checkout main
git pull origin main
git checkout br-seu-nome
git merge main
Isso evita conflitos e garante que você está trabalhando com a versão mais recente.

💡 Faça isso antes de começar uma nova tarefa! 

🧹 8. Boas práticas de organização
✅ Trabalhe apenas na sua branch (br-seu-nome).
✅ Commits curtos, frequentes e com mensagens claras.
✅ Sempre atualize sua branch com a main antes de novas alterações:
bash


1
git pull origin main
✅ Após um Pull Request ser aprovado, todos devem atualizar seu código local com git pull origin main.
💼 Padrão de branches — Projeto Nexus
Lari
br-lari
Saaby
br-saaby
Well
br-well
Natan
br-natan
Mavi
br-mavi

📌 Use exatamente esse nome na sua branch e nos commits. 

🪶 Dica final
Commits bem escritos são a memória do seu projeto.
Eles ajudam na revisão, depuração e no onboarding de novos membros. 

Mantenha o foco na clareza, consistência e colaboração!

Documento criado para o Projeto Nexus — Equipe de Desenvolvimento
Atualizado em: Abril de 2025

