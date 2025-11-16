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
