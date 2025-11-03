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

// Notification button
const notificationBtn = document.querySelector(".notification-btn")
if (notificationBtn) {
  notificationBtn.addEventListener("click", () => {
    alert("Você tem 2 novas notificações!")
  })
}
