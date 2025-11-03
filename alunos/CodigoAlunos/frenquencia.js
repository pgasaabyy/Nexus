// Modal functionality
const justifyBtn = document.getElementById("justifyBtn")
const modal = document.getElementById("justificationModal")
const modalBackBtn = document.querySelector(".modal-back-btn")
const fileInput = document.getElementById("document")
const fileLabel = document.querySelector(".file-hint")

if (justifyBtn) {
  justifyBtn.addEventListener("click", () => {
    modal.classList.add("active")
  })
}

if (modalBackBtn) {
  modalBackBtn.addEventListener("click", () => {
    modal.classList.remove("active")
  })
}

// Close modal when clicking outside
modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.classList.remove("active")
  }
})

// File upload handling
if (fileInput) {
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      fileLabel.textContent = e.target.files[0].name
    } else {
      fileLabel.textContent = "Nenhum Arquivo selecionado"
    }
  })
}

// Form submission
const submitBtn = document.querySelector(".btn-submit")
if (submitBtn) {
  submitBtn.addEventListener("click", (e) => {
    e.preventDefault()
    const justification = document.getElementById("justification").value
    const absenceDate = document.getElementById("absenceDate").value

    if (!justification || !absenceDate) {
      alert("Por favor, preencha todos os campos obrigatórios.")
      return
    }

    alert("Justificativa enviada com sucesso!")
    modal.classList.remove("active")

    // Reset form
    document.getElementById("justification").value = ""
    document.getElementById("document").value = ""
    fileLabel.textContent = "Nenhum Arquivo selecionado"
  })
}
