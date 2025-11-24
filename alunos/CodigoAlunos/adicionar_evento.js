document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-event-form');
    
    // Adiciona um "listener" para o evento de submit do formulário
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        // Coleta os dados
        const eventName = document.getElementById('event-name').value;
        const eventDay = document.getElementById('event-day').value;
        const eventMonth = document.getElementById('event-month').options[document.getElementById('event-month').selectedIndex].text;
        const eventType = document.getElementById('event-type').options[document.getElementById('event-type').selectedIndex].text;
        const eventTime = document.getElementById('event-time').value;

        // Cria a mensagem de resumo
        let message = `Evento Cadastrado com Sucesso!\n\n`;
        message += `Nome: ${eventName}\n`;
        message += `Data: ${eventDay} de ${eventMonth}\n`;
        message += `Tipo: ${eventType}\n`;
        message += `Horário: ${eventTime || 'Não informado'}\n`;

        alert(message);
        
        // Redireciona de volta para o calendário
        window.location.href = 'calendario.html'; 
    });
});