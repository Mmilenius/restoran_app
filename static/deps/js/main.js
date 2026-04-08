document.addEventListener('DOMContentLoaded', function() {

    // 1. МОБІЛЬНЕ МЕНЮ
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 2. ПЛАВНИЙ СКРОЛ КАТЕГОРІЙ У МЕНЮ (При кліку)
    const categoryLinks = document.querySelectorAll('.category-scroll-link');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const categorySlug = this.getAttribute('data-category');
            const targetElement = document.getElementById('category-' + categorySlug);

            if (targetElement) {
                const y = targetElement.getBoundingClientRect().top + window.scrollY - 100;
                window.scrollTo({top: y, behavior: 'smooth'});
            }
        });
    });

    // 2.5 АВТОМАТИЧНА ПІДСВІТКА ПРИ СКРОЛІ (ScrollSpy)
    const sections = document.querySelectorAll('div[id^="category-"]');
    const allDishesLink = document.getElementById('all-dishes-link');

    if (sections.length > 0) {
        window.addEventListener('scroll', function() {
            let current = '';
            // Беремо позицію скролу + відступ на висоту хедера (150px)
            const scrollY = window.scrollY + 150;

            // Визначаємо, яка секція зараз на екрані
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;

                if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                    current = section.getAttribute('id').replace('category-', '');
                }
            });

            let isAnyCategoryActive = false;

            // Змінюємо кольори кнопок у лівому меню
            categoryLinks.forEach(link => {
                link.classList.remove('bg-primary', 'text-white', 'shadow-md');
                link.classList.add('text-gray-700');

                if (link.getAttribute('data-category') === current) {
                    link.classList.remove('text-gray-700');
                    link.classList.add('bg-primary', 'text-white', 'shadow-md');
                    isAnyCategoryActive = true;
                }
            });

            // Керуємо кнопкою "Всі страви"
            if (allDishesLink) {
                if (isAnyCategoryActive) {
                    // Якщо активна якась категорія, знімаємо підсвітку з "Всі страви"
                    allDishesLink.classList.remove('bg-primary', 'text-white', 'shadow-md');
                    allDishesLink.classList.add('text-gray-700');
                } else if (window.scrollY < 200) {
                    // Якщо ми на самому верху сторінки, підсвічуємо "Всі страви"
                    allDishesLink.classList.remove('text-gray-700');
                    allDishesLink.classList.add('bg-primary', 'text-white', 'shadow-md');
                }
            }
        });
    }

    // 3. ДОДАВАННЯ СТРАВИ В КОРЗИНУ
    const addButtons = document.querySelectorAll(".add-btn");
    addButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const dishId = this.getAttribute("data-dish-id");
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie("csrftoken");

            fetch("/cart/add/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ dish_id: dishId, quantity: 1 })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const counter = document.getElementById("cart-count");
                    if(counter) counter.textContent = data.cart_total_items;

                    const modal = document.getElementById("cartModal");
                    if (modal && !modal.classList.contains("hidden")) {
                        fetch("/cart/").then(res => res.text()).then(html => {
                            document.getElementById("cart-container").innerHTML = html;
                        });
                    }

                    const originalText = this.innerHTML;
                    this.innerHTML = "✓ ДОДАНО";
                    this.classList.add("bg-green-500", "text-white");
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.remove("bg-green-500", "text-white");
                    }, 1500);
                } else {
                    alert("Помилка при додаванні: " + data.message);
                }
            })
            .catch(err => console.error("Помилка AJAX:", err));
        });
    });

    // 4. ЛОГІКА СТОРІНКИ ДЕТАЛЕЙ СТРАВИ (МОДАЛКА)
    const detailOverlay = document.getElementById('dish-modal-overlay');
    if (detailOverlay) {
        let currentQuantity = 1;
        const quantityDisplay = document.getElementById('quantity');
        const totalPriceDisplay = document.getElementById('total-price');
        const addDetailBtn = document.querySelector('.add-detail-btn');

        const basePriceStr = addDetailBtn ? addDetailBtn.getAttribute('data-price') : "0";
        const basePrice = parseFloat(basePriceStr.replace(',', '.')) || 0;

        document.getElementById('btn-decrease')?.addEventListener('click', function() {
            if (currentQuantity > 1) {
                currentQuantity--;
                updateDisplay();
            }
        });

        document.getElementById('btn-increase')?.addEventListener('click', function() {
            currentQuantity++;
            updateDisplay();
        });

        function updateDisplay() {
            if (quantityDisplay) quantityDisplay.textContent = currentQuantity;
            if (totalPriceDisplay) totalPriceDisplay.textContent = (basePrice * currentQuantity).toFixed(0);
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') window.history.back();
        });
        detailOverlay.addEventListener('click', function(e) {
            if (e.target === this) window.history.back();
        });

        if (addDetailBtn) {
            addDetailBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const dishId = this.getAttribute('data-dish-id');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie("csrftoken");

                fetch("/cart/add/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        dish_id: dishId,
                        quantity: currentQuantity
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const counter = document.getElementById("cart-count");
                        if(counter) counter.textContent = data.cart_total_items;

                        this.innerHTML = '<i class="fas fa-check"></i> Додано';
                        this.classList.replace('bg-primary', 'bg-green-500');
                        this.classList.replace('hover:bg-[#6B3410]', 'hover:bg-green-600');

                        setTimeout(() => {
                            window.history.back();
                        }, 1000);
                    } else {
                        alert("Помилка при додаванні");
                    }
                })
                .catch(err => console.error("Помилка AJAX:", err));
            });
        }
    }

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
});

// 5. ВІДКРИТТЯ/ЗАКРИТТЯ МОДАЛКИ КОРЗИНИ
window.toggleCartModal = function() {
    const modal = document.getElementById("cartModal");
    if (modal) {
        if (modal.classList.contains("hidden")) {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
            fetch("/cart/")
                .then(res => res.text())
                .then(html => {
                    const container = document.getElementById("cart-container");
                    if (container) container.innerHTML = html;
                });
        } else {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
        }
    }
};

// 6. ЛОГІКА ОФОРМЛЕННЯ ЗАМОВЛЕННЯ (AJAX)
    const orderForm = document.getElementById('order-form');
    if (orderForm) {
        orderForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const tableNumber = formData.get('table_number');
            const notes = formData.get('notes');

            // Отримуємо токен (використовуємо функцію getCookie, яка вже є в твоєму main.js)
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie("csrftoken");

            fetch('/orders/api/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    table_number: parseInt(tableNumber),
                    notes: notes
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert('Помилка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Сталася помилка при оформленні замовлення');
            });
        });
    }

// 7. ЛОГІКА КОРЗИНИ (Зміна кількості та видалення всередині модалки)
    document.addEventListener('click', function(e) {

        // Допоміжна функція для отримання токена
        const getCsrfToken = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie("csrftoken");

        // Зменшити / Збільшити кількість
        if (e.target.closest('.cart-update-btn')) {
            const btn = e.target.closest('.cart-update-btn');
            const dishId = btn.getAttribute('data-dish-id');
            const action = btn.getAttribute('data-action');
            const input = document.querySelector(`.cart-quantity-input[data-dish-id="${dishId}"]`);

            if (input) {
                let currentVal = parseInt(input.value);
                let newVal = action === 'increase' ? currentVal + 1 : currentVal - 1;

                if (newVal < 1) {
                    removeCartItem(dishId);
                } else {
                    updateCartItem(dishId, newVal);
                }
            }
        }

        // Ручне введення кількості
        if (e.target.classList.contains('cart-quantity-input')) {
            e.target.addEventListener('change', function() {
                const dishId = this.getAttribute('data-dish-id');
                const newVal = parseInt(this.value);
                if (newVal < 1) {
                    removeCartItem(dishId);
                } else {
                    updateCartItem(dishId, newVal);
                }
            }, { once: true });
        }

        // Видалення товару
        if (e.target.closest('.cart-remove-btn')) {
            const btn = e.target.closest('.cart-remove-btn');
            const dishId = btn.getAttribute('data-dish-id');
            if (confirm('Видалити цей товар з корзини?')) {
                removeCartItem(dishId);
            }
        }

        // Функція: Оновити кількість (AJAX)
        function updateCartItem(dishId, quantity) {
            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ dish_id: dishId, quantity: quantity })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    refreshCartUI();
                } else {
                    alert(data.message);
                }
            });
        }

        // Функція: Видалити товар (AJAX)
        function removeCartItem(dishId) {
            fetch('/cart/remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ dish_id: dishId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    refreshCartUI();
                } else {
                    alert(data.message);
                }
            });
        }

        // Функція: Перемалювати корзину
        function refreshCartUI() {
            fetch("/cart/")
                .then(res => res.text())
                .then(html => {
                    const container = document.getElementById("cart-container");
                    if (container) container.innerHTML = html;

                    // Оновлюємо цифру на значку корзини в хедері (якщо треба, треба запит на отримання цифри, але зазвичай бекенд повертає її в JSON.
                    // Щоб не робити зайвих запитів, оновимо сторінку або можна зробити окремий endpoint. Для надійності оновлюємо сторінку, якщо корзина порожня)
                    if (html.includes('Корзина порожня')) {
                        const counter = document.getElementById("cart-count");
                        if(counter) counter.textContent = '0';
                    }
                });
        }
    });