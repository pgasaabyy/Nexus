// Elementos do DOM
const toggleBtn = document.getElementById('chatbot-toggle');
const chatWindow = document.getElementById('chatbot-window');
const closeBtn = document.getElementById('chatbot-close');
const chatInput = document.getElementById('chatbot-input');
const sendBtn = document.getElementById('chatbot-send');
const messagesContainer = document.getElementById('chatbot-messages');
const chatIcon = document.getElementById('chat-icon');
const closeIcon = document.getElementById('close-icon');

// Estado do chatbot
let isOpen = false;

// Função para alternar visibilidade do chatbot
function toggleChat() {
    isOpen = !isOpen;
    
    if (isOpen) {
        chatWindow.classList.remove('hidden');
        chatIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
        chatInput.focus();
    } else {
        chatWindow.classList.add('hidden');
        chatIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
    }
}

// Função para adicionar mensagem
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll para última mensagem
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Função para enviar mensagem
function sendMessage() {
    const message = chatInput.value.trim();
    
    if (message) {
        // Adicionar mensagem do usuário
        addMessage(message, true);
        chatInput.value = '';
        
        // Simular resposta do bot após 1 segundo
        setTimeout(() => {
            addMessage('Obrigado pela sua mensagem! Nossa equipe entrará em contato em breve.');
        }, 1000);
    }
}

// Event listeners
toggleBtn.addEventListener('click', toggleChat);
closeBtn.addEventListener('click', toggleChat);
sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Fechar chatbot ao clicar fora
document.addEventListener('click', (e) => {
    if (isOpen && 
        !chatWindow.contains(e.target) && 
        !toggleBtn.contains(e.target)) {
        toggleChat();
    }
});

console.log('ChatBot NEXUS inicializado!');
