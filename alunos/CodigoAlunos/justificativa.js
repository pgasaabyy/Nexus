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
