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

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-event-form');
    
    // Adiciona um "listener" para o evento de submit do formulário
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        // Coleta os dados
        const eventName = document.getElementById('event-name').value;
        const eventDay = document.getElementById('event-day').value;
        const eventMonth = document.getElementById('event-month').options[document.getElementById('event-month').selectedIndex].text;
        const eventType = document.getElementById('event-type').options[document.getElementById('event-type').selectedIndex].text;
        const eventTime = document.getElementById('event-time').value;

        // Cria a mensagem de resumo
        let message = `Evento Cadastrado com Sucesso!\n\n`;
        message += `Nome: ${eventName}\n`;
        message += `Data: ${eventDay} de ${eventMonth}\n`;
        message += `Tipo: ${eventType}\n`;
        message += `Horário: ${eventTime || 'Não informado'}\n`;

        alert(message);
        
        // Redireciona de volta para o calendário
        window.location.href = 'calendario.html'; 
    });
});

const monthSelector = document.getElementById("monthSelector")
const monthYearDisplay = document.getElementById("calendarMonthYear")
const calendarGrid = document.getElementById("calendarGrid")
const prevMonthBtn = document.getElementById("prevMonth")
const nextMonthBtn = document.getElementById("nextMonth")
const holidayLegends = document.getElementById("holidayLegends")

const months = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
]

const holidays2025 = {
  "2025-01-01": { name: "Ano Novo", color: "#003366" },
  "2025-01-25": { name: "Aniversário de São Paulo", color: "#5DADE2" },
  "2025-02-12": { name: "Início do Carnaval", color: "#FF6B9D" },
  "2025-03-04": { name: "Quarta-feira de Cinzas", color: "#003366" },
  "2025-04-18": { name: "Sexta-feira Santa", color: "#5DADE2" },
  "2025-04-20": { name: "Páscoa", color: "#FF6B9D" },
  "2025-04-21": { name: "Tiradentes", color: "#003366" },
  "2025-05-01": { name: "Dia do Trabalho", color: "#5DADE2" },
  "2025-06-19": { name: "Corpus Christi", color: "#FF6B9D" },
  "2025-09-07": { name: "Independência do Brasil", color: "#003366" },
  "2025-10-12": { name: "Nossa Senhora Aparecida", color: "#5DADE2" },
  "2025-11-02": { name: "Finados", color: "#FF6B9D" },
  "2025-11-15": { name: "Proclamação da República", color: "#003366" },
  "2025-11-20": { name: "Consciência Negra", color: "#5DADE2" },
  "2025-12-25": { name: "Natal", color: "#FF6B9D" },
}

let currentMonth = 0 // January
let currentYear = 2025

document.addEventListener("DOMContentLoaded", () => {
  const today = new Date()
  currentMonth = today.getMonth()
  monthSelector.value = currentMonth
  renderCalendar()

// Add event button
  const addEventBtn = document.querySelector(".btn-add-event")
  if (addEventBtn) {
    addEventBtn.addEventListener("click", () => {
      window.location.href = 'adicionar_evento.html'; // Adicionado: Redireciona para a nova página
    })
  }

  // Filter button
  const filterBtn = document.querySelector(".filter-btn")
  if (filterBtn) {
    filterBtn.addEventListener("click", () => {
      alert("Funcionalidade de filtros em desenvolvimento!")
    })
  }
})

if (monthSelector) {
  monthSelector.addEventListener("change", (e) => {
    currentMonth = Number.parseInt(e.target.value)
    renderCalendar()
  })
}

if (prevMonthBtn) {
  prevMonthBtn.addEventListener("click", () => {
    currentMonth--
    if (currentMonth < 0) {
      currentMonth = 11
      currentYear--
    }
    monthSelector.value = currentMonth
    renderCalendar()
  })
}

if (nextMonthBtn) {
  nextMonthBtn.addEventListener("click", () => {
    currentMonth++
    if (currentMonth > 11) {
      currentMonth = 0
      currentYear++
    }
    monthSelector.value = currentMonth
    renderCalendar()
  })
}

function renderCalendar() {
  if (!calendarGrid) return

  monthYearDisplay.textContent = `${months[currentMonth]} ${currentYear}`

  const firstDay = new Date(currentYear, currentMonth, 1).getDay()
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate()
  const today = new Date()

  let daysHTML = ""

  // Empty cells for days before the first day of month
  for (let i = 0; i < firstDay; i++) {
    daysHTML += '<div class="calendar-day empty"></div>'
  }

  // Days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`
    const isToday = day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()

    const holiday = holidays2025[dateStr]
    let dayClass = "calendar-day"
    if (isToday) dayClass += " today"
    if (holiday) dayClass += " holiday"

    let dayStyle = ""
    if (holiday) {
      dayStyle = `style="border-left: 4px solid ${holiday.color}"`
    }

    daysHTML += `<div class="${dayClass}" ${dayStyle} title="${holiday ? holiday.name : ""}">${day}</div>`
  }

  calendarGrid.innerHTML = daysHTML

  // Render holiday legends for current month
  renderHolidayLegends()
}

function renderHolidayLegends() {
  if (!holidayLegends) return

  const monthHolidays = Object.entries(holidays2025).filter(([date, info]) => {
    const [year, month] = date.split("-")
    return Number.parseInt(year) === currentYear && Number.parseInt(month) === currentMonth + 1
  })

  if (monthHolidays.length === 0) {
    holidayLegends.innerHTML = '<div class="legend-item-cal"><span>Nenhum feriado neste mês</span></div>'
    return
  }

  const legendsHTML = monthHolidays
    .map(([date, info]) => {
      const day = Number.parseInt(date.split("-")[2])
      return `
        <div class="legend-item-cal">
          <div class="legend-dot" style="background-color: ${info.color};"></div>
          <span>${day} - ${info.name}</span>
        </div>
      `
    })
    .join("")

  holidayLegends.innerHTML = legendsHTML
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Funcionalidade do Painel de Notificações
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');

    if (notificationBtn && notificationPanel) {
        notificationBtn.addEventListener('click', (e) => {
            // Previne que o clique feche imediatamente
            e.stopPropagation();
            notificationPanel.classList.toggle('hidden');
        });

        // Fecha o painel se o usuário clicar em qualquer outro lugar
        document.addEventListener('click', (e) => {
            if (notificationPanel && !notificationPanel.contains(e.target) && !notificationBtn.contains(e.target)) {
                notificationPanel.classList.add('hidden');
            }
        });
    }

    // ... (Outras funcionalidades do aluno.js virão aqui)
});

document.addEventListener('DOMContentLoaded', () => {
    // ... (código do painel de notificações acima) ...

    // 2. Funcionalidade de Edição de Foto (Autosubmit)
    const fotoInput = document.getElementById('foto-input');
    if (fotoInput) {
        fotoInput.addEventListener('change', () => {
            document.getElementById('foto-form').submit();
        });
    }

    // 3. Funcionalidade de Edição de Nome de Usuário (Toggle)
    window.toggleEdit = (type) => {
        if (type === 'username') {
            const display = document.getElementById('username-display');
            const form = document.getElementById('username-form');
            
            // Toggle visibility
            display.classList.toggle('hidden');
            form.classList.toggle('hidden');

            // Foco no campo de input quando o formulário aparece
            if (!form.classList.contains('hidden')) {
                form.querySelector('input[name="username"]').focus();
            }

            // Adiciona evento de Cancelar
            const cancelBtn = form.querySelector('.cancel-btn');
            cancelBtn.onclick = () => {
                display.classList.remove('hidden');
                form.classList.add('hidden');
            };
        }
    };
});


