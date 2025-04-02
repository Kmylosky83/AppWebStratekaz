document.addEventListener('DOMContentLoaded', function() {
    const kmyToggle = document.getElementById('kmy-toggle');
    const kmyPanel = document.getElementById('kmy-chat-panel');
    const kmyCloseBtn = document.getElementById('kmy-close-btn');
    const kmyMessages = document.getElementById('kmy-messages');
    const kmyInput = document.getElementById('kmy-user-input');
    const kmySendBtn = document.getElementById('kmy-send-btn');
    
    // Respuestas predefinidas para la versión inicial
    const kmyResponses = {
      greeting: [
        "¡Hola! Soy Kmy, tu asistente virtual de StrateKaz. ¿En qué puedo ayudarte?",
        "¡Bienvenido! Estoy aquí para ayudarte con tus sistemas de gestión. ¿Qué necesitas?"
      ],
      fallback: [
        "Estoy aprendiendo sobre ese tema. ¿Puedo ayudarte con algo más sobre sistemas de gestión?",
        "No tengo información específica sobre eso aún. ¿Te gustaría saber sobre SG-SST, ISO o PESV?"
      ]
    };
    
    // Detectar contexto actual
    function getCurrentContext() {
      const path = window.location.pathname;
      
      if (path.includes('/dashboard')) {
        return 'dashboard';
      } else if (path.includes('/formacion')) {
        return 'formacion';
      } else if (path.includes('/herramientas')) {
        return 'herramientas';
      } else {
        return 'general';
      }
    }
    
    // Agregar mensaje de bienvenida
    function addWelcomeMessage() {
      const welcomeMsg = document.createElement('div');
      welcomeMsg.className = 'kmy-message assistant';
      welcomeMsg.textContent = kmyResponses.greeting[Math.floor(Math.random() * kmyResponses.greeting.length)];
      kmyMessages.appendChild(welcomeMsg);
    }
    
    // Agregar mensaje al chat
    function addMessage(text, isUser = false) {
      const msg = document.createElement('div');
      msg.className = `kmy-message ${isUser ? 'user' : 'assistant'}`;
      msg.textContent = text;
      
      // Si es mensaje del asistente, agregar botones de feedback
      if (!isUser) {
        const msgId = Date.now().toString();
        msg.dataset.id = msgId;
        
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'message-feedback';
        
        const thumbsUp = document.createElement('button');
        thumbsUp.className = 'feedback-btn';
        thumbsUp.dataset.value = 'helpful';
        thumbsUp.innerHTML = '<i class="fas fa-thumbs-up"></i>';
        
        const thumbsDown = document.createElement('button');
        thumbsDown.className = 'feedback-btn';
        thumbsDown.dataset.value = 'not-helpful';
        thumbsDown.innerHTML = '<i class="fas fa-thumbs-down"></i>';
        
        feedbackDiv.appendChild(thumbsUp);
        feedbackDiv.appendChild(thumbsDown);
        msg.appendChild(feedbackDiv);
      }
      
      kmyMessages.appendChild(msg);
      kmyMessages.scrollTop = kmyMessages.scrollHeight;
    }
    
    // Obtener respuesta (versión inicial)
    function getResponse(input) {
      // En la versión inicial, solo usar respuestas predefinidas
      return kmyResponses.fallback[Math.floor(Math.random() * kmyResponses.fallback.length)];
    }
    
    // Event Listeners
    kmyToggle.addEventListener('click', function() {
      kmyPanel.style.display = 'flex';
      if (kmyMessages.children.length === 0) {
        addWelcomeMessage();
      }
    });
    
    kmyCloseBtn.addEventListener('click', function() {
      kmyPanel.style.display = 'none';
    });
    
    kmySendBtn.addEventListener('click', function() {
      sendMessage();
    });
    
    kmyInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
    
    function sendMessage() {
      const userInput = kmyInput.value.trim();
      if (userInput) {
        addMessage(userInput, true);
        kmyInput.value = '';
        
        // Simular respuesta con pequeño delay
        setTimeout(() => {
          const response = getResponse(userInput);
          addMessage(response);
        }, 500);
      }
    }
    
    // Capturar feedback
    document.addEventListener('click', function(e) {
      if (e.target.closest('.feedback-btn')) {
        const btn = e.target.closest('.feedback-btn');
        const value = btn.dataset.value;
        const messageEl = btn.closest('.kmy-message');
        
        // Actualizar UI
        messageEl.querySelectorAll('.feedback-btn').forEach(b => {
          b.classList.remove('active');
        });
        btn.classList.add('active');
        
        // Aquí se podría enviar el feedback al servidor en el futuro
        console.log('Feedback:', value, 'para mensaje:', messageEl.textContent);
      }
    });
  });