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

// Edit buttons functionality
const editButtons = document.querySelectorAll(".edit-btn")
editButtons.forEach((btn) => {
  btn.addEventListener("click", function () {
    const parent = this.closest(".info-value-with-edit")
    const currentValue = parent.querySelector("span").textContent
    const label = this.closest(".info-item").querySelector("label").textContent

    const newValue = prompt(`Editar ${label}:`, currentValue)
    if (newValue && newValue !== currentValue) {
      parent.querySelector("span").textContent = newValue
      alert("Informação atualizada com sucesso!")
    }
  })
})

// Edit avatar button
const editAvatarBtn = document.querySelector(".edit-avatar-btn")
if (editAvatarBtn) {
  editAvatarBtn.addEventListener("click", () => {
    alert("Funcionalidade de editar foto em desenvolvimento!")
  })
}

// Modal functionality removed - now using separate page
const fileInput = document.getElementById("document")
const fileLabel = document.querySelector(".file-hint")

// File upload handling (kept for potential future use)
if (fileInput) {
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      fileLabel.textContent = e.target.files[0].name
    } else {
      fileLabel.textContent = "Nenhum Arquivo selecionado"
    }
  })
}

document.addEventListener("DOMContentLoaded", () => {
  const backBtn = document.querySelector(".back-btn")

  if (backBtn) {
    backBtn.addEventListener("click", () => {
      window.location.href = "index.html"
    })
  }
})

// File upload handling
const documentoInput = document.getElementById('documento');
const fileNameSpan = document.querySelector('.file-name');

if (documentoInput && fileNameSpan) {
    documentoInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameSpan.textContent = e.target.files[0].name;
        } else {
            fileNameSpan.textContent = 'Nenhum Arquvi selecionado';
        }
    });
}

// Form submission
const form = document.getElementById('justificativaForm');
if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const justificativa = document.getElementById('justificativa').value;
        const diaFalta = document.getElementById('diaFalta').value;
        const documento = documentoInput.files[0];

        if (!justificativa.trim()) {
            alert('Por favor, preencha a justificativa.');
            return;
        }

        if (!diaFalta) {
            alert('Por favor, selecione o dia da falta.');
            return;
        }

        // Success message
        alert('Justificativa enviada com sucesso!');
        
        // Redirect back to frequency page
        window.location.href = 'frenquencia.html';
    });
}
