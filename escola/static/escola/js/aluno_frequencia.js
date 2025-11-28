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