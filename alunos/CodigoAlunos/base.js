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
