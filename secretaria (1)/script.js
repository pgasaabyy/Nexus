// ===== FUNCIONALIDADES GERAIS DO DASHBOARD =====

// Ativa abas/tabs
document.querySelectorAll(".tab-button").forEach((button) => {
  button.addEventListener("click", function () {
    const tabName = this.getAttribute("data-tab")

    // Remove classe ativa de todos os botões
    document.querySelectorAll(".tab-button").forEach((btn) => {
      btn.classList.remove("active")
    })

    // Adiciona classe ativa ao botão clicado
    this.classList.add("active")

    // Esconde todos os tabs
    document.querySelectorAll(".tab-content").forEach((tab) => {
      tab.style.display = "none"
    })

    // Mostra o tab selecionado
    const selectedTab = document.getElementById(tabName)
    if (selectedTab) {
      selectedTab.style.display = "table-row-group"
    }
  })
})

// ===== BUSCA EM TABELAS =====

// Busca na tabela de alunos
const searchAlunos = document.getElementById("searchAlunos")
if (searchAlunos) {
  searchAlunos.addEventListener("keyup", function () {
    const searchValue = this.value.toLowerCase()
    const rows = document.querySelectorAll("#tbody-alunos tr")

    rows.forEach((row) => {
      const text = row.textContent.toLowerCase()
      row.style.display = text.includes(searchValue) ? "" : "none"
    })
  })
}

// Busca na tabela de professores
const searchProfessores = document.getElementById("searchProfessores")
if (searchProfessores) {
  searchProfessores.addEventListener("keyup", function () {
    const searchValue = this.value.toLowerCase()
    const rows = document.querySelectorAll("#tbody-professores tr")

    rows.forEach((row) => {
      const text = row.textContent.toLowerCase()
      row.style.display = text.includes(searchValue) ? "" : "none"
    })
  })
}

// ===== NAVEGAÇÃO ATIVA NO SIDEBAR =====

// Ativa o link correto no sidebar baseado na página atual
document.addEventListener("DOMContentLoaded", () => {
  const currentPath = window.location.pathname
  const navItems = document.querySelectorAll(".nav-item")

  navItems.forEach((item) => {
    if (currentPath.includes(item.getAttribute("href"))) {
      item.classList.add("active")
    } else {
      item.classList.remove("active")
    }
  })
})

// ===== AÇÕES DE ÍCONES =====

// Adiciona feedback visual ao clicar em ícones de ação
document.querySelectorAll(".action-icons i").forEach((icon) => {
  icon.addEventListener("click", () => {
    console.log("Ação executada")
  })
})

// ===== LOGOUT =====

document.querySelectorAll(".nav-item.logout").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault()
    if (confirm("Tem certeza que deseja fazer logout?")) {
      // Aqui você pode redirecionar para a página de login
      console.log("Logout realizado")
    }
  })
})

console.log("Dashboard inicializado com sucesso!")
