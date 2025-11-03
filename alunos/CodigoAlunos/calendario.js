// Month selector functionality
const monthSelector = document.querySelector(".month-selector")
const monthYearDisplay = document.querySelector(".calendar-month-year")

const months = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho,",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
]

if (monthSelector) {
  monthSelector.addEventListener("change", (e) => {
    const monthIndex = Number.parseInt(e.target.value)
    monthYearDisplay.textContent = `${months[monthIndex]} 2025`
  })
}

// Add event button
const addEventBtn = document.querySelector(".btn-add-event")
if (addEventBtn) {
  addEventBtn.addEventListener("click", () => {
    alert("Funcionalidade de adicionar evento em desenvolvimento!")
  })
}

// Filter button
const filterBtn = document.querySelector(".filter-btn")
if (filterBtn) {
  filterBtn.addEventListener("click", () => {
    alert("Filtros disponíveis: 1º-2º ano Professores, 3º Semana de Biologia, 3º+ Prova de Matemática")
  })
}
