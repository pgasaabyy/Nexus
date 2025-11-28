// Smooth scroll para links de navegação
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  })
})

// Adicionar classe ativa no scroll
window.addEventListener("scroll", () => {
  const sections = document.querySelectorAll("section[id]")
  const scrollY = window.pageYOffset

  sections.forEach((section) => {
    const sectionHeight = section.offsetHeight
    const sectionTop = section.offsetTop - 100
    const sectionId = section.getAttribute("id")
    const navLink = document.querySelector(`.nav a[href="#${sectionId}"]`)

    if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
      if (navLink) {
        document.querySelectorAll(".nav a").forEach((link) => {
          link.style.opacity = "0.7"
        })
        navLink.style.opacity = "1"
      }
    }
  })
})

document.addEventListener("DOMContentLoaded", () => {
  const featureCards = document.querySelectorAll(".feature-card")

  // Adiciona efeito de parallax 3D ao mover o mouse
  featureCards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      const centerX = rect.width / 2
      const centerY = rect.height / 2

      const rotateX = (y - centerY) / 20
      const rotateY = (centerX - x) / 20

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`
    })

    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(1000px) rotateX(0) rotateY(0) translateY(0)"
    })

    // Adiciona animação de pulse ao clicar
    card.addEventListener("click", function () {
      this.style.animation = "none"
      setTimeout(() => {
        this.style.animation = "pulse 0.5s ease-out"
      }, 10)
    })
  })
})

// Adiciona animação de pulse ao CSS dinamicamente
const style = document.createElement("style")
style.textContent = `
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
`
document.head.appendChild(style)

// Animação ao aparecer na tela
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -100px 0px",
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1"
      entry.target.style.transform = "translateY(0)"
    }
  })
}, observerOptions)

document.querySelectorAll(".module-card, .dashboard-card, .team-card, .stat-card, .feature-card").forEach((card) => {
  card.style.opacity = "0"
  card.style.transform = "translateY(30px)"
  card.style.transition = "opacity 0.6s ease, transform 0.6s ease"
  observer.observe(card)
})

console.log("NEXUS Sistema inicializado!")