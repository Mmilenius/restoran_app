document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('booking-form');
    const dateInput = document.querySelector('input[name="date"]');
    const timeInput = document.querySelector('input[name="time"]');
    const durationInput = document.querySelector('input[name="duration"]');
    const zoneSelect = document.querySelector('select[name="zone"]');

    // Встановлюємо мінімальну дату
    const today = new Date().toISOString().split('T')[0];
    if(dateInput) dateInput.min = today;

    // Перевірка доступності
    function checkAvailability() {
        const date = dateInput?.value;
        const time = timeInput?.value;
        const duration = durationInput?.value;
        const zone = zoneSelect?.value;

        if (date && time) {
            fetch(`/booking/check-availability/?date=${date}&time=${time}&duration=${duration}&zone=${zone}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.available) {
                        alert('Увага: ' + data.message);
                    }
                });
        }
    }

    if(dateInput) dateInput.addEventListener('change', checkAvailability);
    if(timeInput) timeInput.addEventListener('change', checkAvailability);
    if(durationInput) durationInput.addEventListener('change', checkAvailability);
    if(zoneSelect) zoneSelect.addEventListener('change', checkAvailability);

    // Відправка форми
    if(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            // БЕРЕМО CSRF ТОКЕН ІЗ САМОЇ ФОРМИ:
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/booking/api/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken // Використовуємо знайдену змінну
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert('Помилка: ' + data.message);
                    if (data.errors) {
                        console.error('Validation errors:', data.errors);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Сталася помилка при бронюванні');
            });
        });
    }
});