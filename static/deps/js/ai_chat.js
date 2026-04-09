document.addEventListener('DOMContentLoaded', function() {
    // 1. Отримуємо елементи
    const aiToggleBtn = document.getElementById('ai-toggle-btn');
    const aiCloseBtn = document.getElementById('ai-close-btn');
    const aiChatBox = document.getElementById('ai-chat-box');
    const aiInput = document.getElementById('ai-input');
    const aiSendBtn = document.getElementById('ai-send-btn');
    const aiMessages = document.getElementById('ai-messages');

    // Перевіряємо, чи є віджет на сторінці
    if (!aiToggleBtn || !aiChatBox) return;

    // 2. Функція отримання CSRF токена (потрібна для Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 3. Відкрити/Закрити чат
    const toggleChat = () => {
        if (aiChatBox.classList.contains('hidden')) {
            aiChatBox.classList.remove('hidden');
            aiChatBox.classList.add('flex');
            aiInput.focus();
        } else {
            aiChatBox.classList.add('hidden');
            aiChatBox.classList.remove('flex');
        }
    };

    aiToggleBtn.addEventListener('click', toggleChat);
    aiCloseBtn.addEventListener('click', toggleChat);

    // 4. Функція для малювання повідомлень
    function appendMessage(text, sender, isLoading = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = "flex gap-2 w-full mt-2";
        const uniqueId = 'msg-' + Date.now();
        msgDiv.id = uniqueId;

        if (sender === 'user') {
            msgDiv.classList.add('justify-end');
            msgDiv.innerHTML = `
                <div class="bg-primary text-white p-3 rounded-2xl rounded-tr-none shadow-sm text-sm max-w-[85%]">
                    ${text}
                </div>
            `;
        } else {
            msgDiv.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-primary flex-shrink-0 flex justify-center items-center text-white text-xs mt-1">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="bg-white border border-gray-100 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-gray-700 max-w-[85%]">
                    ${text}
                </div>
            `;
        }

        aiMessages.appendChild(msgDiv);
        aiMessages.scrollTop = aiMessages.scrollHeight; // Автоматичний скрол вниз
        return uniqueId;
    }

    // 5. Відправка повідомлення на сервер
    const sendMessage = () => {
        const text = aiInput.value.trim();
        if (!text) return;

        // Показуємо повідомлення юзера
        appendMessage(text, 'user');
        aiInput.value = '';

        // Показуємо індикатор завантаження ШІ
        const loadingId = appendMessage('<i class="fas fa-circle-notch fa-spin text-gray-400"></i>', 'ai', true);

        // Звертаємося до нашого нового додатку ai_assistant
        fetch('/ai/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify({ message: text })
        })
        .then(response => response.json())
        .then(data => {
            // Видаляємо індикатор завантаження
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) loadingMsg.remove();

            // Показуємо відповідь
            if (data.success) {
                appendMessage(data.reply, 'ai');
            } else {
                appendMessage("Вибачте, сталася помилка: " + (data.error || "Невідома помилка"), 'ai');
            }
        })
        .catch(err => {
            console.error("AI Error:", err);
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) loadingMsg.remove();
            appendMessage("Не вдалося підключитися до сервера.", 'ai');
        });
    };

    // Відправка по кліку на кнопку або клавіші Enter
    aiSendBtn.addEventListener('click', sendMessage);
    aiInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});