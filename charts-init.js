document.addEventListener('DOMContentLoaded', function () {
    // Gráfico 1: Desempenho por Turmas (Barras)
    const ctxDesempenho = document.getElementById('desempenhoTurmasChart');
    if (ctxDesempenho) {
        new Chart(ctxDesempenho, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
                datasets: [{
                    label: 'Aprovados',
                    data: [85, 90, 88, 92, 95],
                    backgroundColor: '#28a745', // Verde
                    borderRadius: 4,
                }, {
                    label: 'Reprovados',
                    data: [15, 10, 12, 8, 5],
                    backgroundColor: '#dc3545', // Vermelho
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true },
                    y: { stacked: true, beginAtZero: true, max: 100 }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // Gráfico 2: Frequência Semanal (Linha)
    const ctxFrequencia = document.getElementById('frequenciaSemanalChart');
    if (ctxFrequencia) {
        new Chart(ctxFrequencia, {
            type: 'line',
            data: {
                labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
                datasets: [{
                    label: 'Frequência Média',
                    data: [95, 98, 99, 97, 96],
                    borderColor: '#092F76', // Azul Escuro
                    backgroundColor: 'rgba(9, 47, 118, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: false, max: 100 }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
});
