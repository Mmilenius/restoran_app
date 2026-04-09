document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('booking-form');
    const dateInput = document.querySelector('input[name="date"]');
    const timeInput = document.querySelector('input[name="time"]');
    const durationInput = document.querySelector('input[name="duration"]');
    const hiddenTableInput = document.getElementById('selected-table-id');
    const tableButtons = document.querySelectorAll('.table-btn');

    // Встановлюємо мінімальну дату (сьогодні)
    if(dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
    }

    // 1. ОНОВЛЕННЯ ВІЗУАЛУ (перефарбовування столика при кліку)
    function updateSelectionVisuals() {
        tableButtons.forEach(btn => {
            if (btn.disabled) return; // Пропускаємо зайняті столи (вони сірі)

            const tableId = btn.getAttribute('data-table-id');
            const isVip = btn.getAttribute('data-vip') === 'true';
            const textSpans = btn.querySelectorAll('.table-info');

            // Скидаємо класи (залишаємо тільки базові)
            btn.className = 'table-btn w-14 h-14 sm:w-16 sm:h-16 border-2 rounded-xl flex flex-col justify-center items-center transition cursor-pointer relative';

            if (hiddenTableInput.value === tableId) {
                // ЯКЩО СТІЛ ОБРАНИЙ - Робимо чорним
                btn.classList.add('bg-gray-900', 'border-gray-900');
                if(textSpans.length > 0) {
                    textSpans[0].className = 'table-info font-bold text-white text-base sm:text-lg';
                    textSpans[1].className = 'table-info text-[10px] sm:text-xs text-gray-300';
                }
            } else {
                // ЯКЩО СТІЛ ВІЛЬНИЙ - Повертаємо оригінальний синій/червоний колір
                if (isVip) {
                    btn.classList.add('border-red-500', 'hover:bg-red-50');
                } else {
                    btn.classList.add('border-blue-400', 'hover:bg-blue-50');
                }
                if(textSpans.length > 0) {
                    textSpans[0].className = 'table-info font-bold text-gray-800 text-base sm:text-lg';
                    textSpans[1].className = 'table-info text-[10px] sm:text-xs text-gray-500';
                }
            }
        });
    }

    // 2. КЛІК ПО СТОЛИКУ
    tableButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.disabled) return; // Зайняті столи клікати не можна

            // Записуємо вибраний ID в приховане поле форми
            hiddenTableInput.value = this.getAttribute('data-table-id');

            // Оновлюємо кольори на екрані (щоб він став чорним)
            updateSelectionVisuals();
        });
    });

    // 3. ПЕРЕВІРКА ЗАЙНЯТОСТІ ПО ЧАСУ (AJAX)
    function fetchAvailability() {
        const date = dateInput?.value;
        const time = timeInput?.value;
        const duration = durationInput?.value;

        if (!date || !time) return;

        fetch(`/booking/check-availability/?date=${date}&time=${time}&duration=${duration}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const occupied = data.occupied_tables; // Масив зайнятих ID (наприклад: [1, 5, 8])

                    tableButtons.forEach(btn => {
                        const tableId = parseInt(btn.getAttribute('data-table-id'));
                        const textSpans = btn.querySelectorAll('.table-info');
                        const xSpan = btn.querySelector('.table-occupied-x');

                        if (occupied.includes(tableId)) {
                            // БЛОКУЄМО СТІЛ (Він зайнятий у цей час)
                            btn.className = 'table-btn w-14 h-14 sm:w-16 sm:h-16 border-2 rounded-xl flex flex-col justify-center items-center relative bg-gray-200 border-gray-300 cursor-not-allowed opacity-70';
                            btn.disabled = true;

                            // Ховаємо цифри, показуємо хрестик
                            if(textSpans) textSpans.forEach(s => s.classList.add('hidden'));
                            if(xSpan) xSpan.classList.remove('hidden');

                            // Якщо цей стіл був обраний нами раніше, але виявився зайнятим - скидаємо вибір
                            if (hiddenTableInput.value == tableId) {
                                hiddenTableInput.value = "";
                            }
                        } else {
                            // ЗВІЛЬНЯЄМО СТІЛ
                            btn.disabled = false;

                            // Показуємо цифри, ховаємо хрестик
                            if(textSpans) textSpans.forEach(s => s.classList.remove('hidden'));
                            if(xSpan) xSpan.classList.add('hidden');
                        }
                    });

                    // Після того як розставили "хрестики", малюємо кольори (чорний для обраного і синій/червоний для вільних)
                    updateSelectionVisuals();
                }
            })
            .catch(error => console.error("Помилка AJAX:", error));
    }

    // Слухаємо зміни дати, часу та кількості годин!
    if(dateInput) dateInput.addEventListener('change', fetchAvailability);
    if(timeInput) timeInput.addEventListener('change', fetchAvailability);
    if(durationInput) durationInput.addEventListener('change', fetchAvailability);

    // Перший запуск при відкритті сторінки (щоб перевірити час за замовчуванням)
    fetchAvailability();

    // 4. ВІДПРАВКА ФОРМИ БРОНЮВАННЯ
    if(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Перевіряємо, чи клікнув користувач на столик
            if (!hiddenTableInput.value) {
                alert('Будь ласка, оберіть вільний столик на карті!');
                return;
            }

            const formData = new FormData(this);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/booking/api/create/', {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': csrfToken }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert('Помилка: ' + data.message);
                }
            })
            .catch(error => console.error("Помилка при бронюванні:", error));
        });
    }
});