document.addEventListener("DOMContentLoaded", () => {
  const backBtn = document.querySelector(".back-btn")

  if (backBtn) {
    backBtn.addEventListener("click", () => {
      window.location.href = "index.html"
    })
  }
})
