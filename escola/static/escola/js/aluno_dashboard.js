// Navigation active state
document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname.split("/").pop() || "base.html"
  const navItems = document.querySelectorAll(".nav-item")

  navItems.forEach((item) => {
    const href = item.getAttribute("href")
    // Check if current page matches or if we're on base.html and link is to base.html
    if (href === currentPage || (currentPage === "" && href === "base.html")) {
      item.classList.add("active")
    } else {
      item.classList.remove("active")
    }
  })
})

// Logout functionality
const logoutBtn = document.querySelector(".logout-btn")
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    if (confirm("Tem certeza que deseja sair?")) {
      alert("Logout realizado com sucesso!")
      // In a real app, this would redirect to login page
    }
  })
}


// adicionar evento
async function addEvent(title, date, type){
  const res = await fetch('/api/events/add/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken()},
    body: JSON.stringify({title, date, event_type: type})
  });
  return res.json();
}

// listar eventos com filtro
async function getEvents(type=null){
  let url = '/api/events/';
  if(type) url += '?type=' + type;
  const res = await fetch(url);
  return res.json();
}

// helper csrftoken (se você estiver usando cookies)
function csrftoken(){
  const name = 'csrftoken';
  const val = document.cookie.split('; ').find(row => row.startsWith(name+'='));
  return val ? val.split('=')[1] : '';
}
// ==== SISTEMA GLOBAL DE NOTIFICAÇÕES ====

// Elementos
const notifBtn = document.querySelector('.notification-btn');
const notifPanel = document.querySelector('.notification-panel');
const notifList = document.getElementById('notifList');

// Alternar painel ao clicar
notifBtn.addEventListener('click', () => {
    notifPanel.classList.toggle('hidden');
});

// Fechar ao clicar fora
document.addEventListener('click', (e) => {
    if (!notifBtn.contains(e.target) && !notifPanel.contains(e.target)) {
        notifPanel.classList.add('hidden');
    }
});

// ------------------------------
// 1. Ler avisos da página (se existir)
// ------------------------------
function lerAvisosDaPagina() {
    const avisos = document.querySelectorAll('.aviso-item');
    const lista = [];

    avisos.forEach(aviso => {
        lista.push({
            dia: aviso.querySelector('.date-day').innerText,
            mes: aviso.querySelector('.date-month').innerText,
            titulo: aviso.querySelector('.aviso-title').innerText,
            subtitulo: aviso.querySelector('.aviso-subtitle').innerText
        });
    });

    return lista;
}

// ------------------------------
// 2. Salvar avisos no localStorage
// ------------------------------
function salvarAvisosGlobal(avisos) {
    if (avisos.length > 0) {
        localStorage.setItem('avisosEscola', JSON.stringify(avisos));
    }
}

// ------------------------------
// 3. Carregar avisos do localStorage
// ------------------------------
function carregarAvisosGlobais() {
    const dados = localStorage.getItem('avisosEscola');
    return dados ? JSON.parse(dados) : [];
}

// ------------------------------
// 4. Criar item no sino
// ------------------------------
function criarItemNotificacao(aviso) {
    const item = document.createElement('div');
    item.classList.add('notif-item');

    item.innerHTML = `
        <div class="notif-date">
            <div class="notif-day">${aviso.dia}</div>
            <div class="notif-month">${aviso.mes}</div>
        </div>
        <div class="notif-text">
            <div class="notif-title-item">${aviso.titulo}</div>
            <div class="notif-sub">${aviso.subtitulo}</div>
        </div>
    `;

    notifList.appendChild(item);
}

// ------------------------------
// 5. Mostrar notificações no sino
// ------------------------------
function mostrarNotificacoes() {
    notifList.innerHTML = "";
    const avisos = carregarAvisosGlobais();
    avisos.forEach(aviso => criarItemNotificacao(aviso));
}

// ------------------------------
// 6. Executar no carregamento da página
// ------------------------------

// Se esta página tiver avisos, salva eles
const avisosDaPagina = lerAvisosDaPagina();
if (avisosDaPagina.length > 0) {
    salvarAvisosGlobal(avisosDaPagina);
}

// Sempre mostrar notificações
mostrarNotificacoes();
