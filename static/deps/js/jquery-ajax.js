// Коли HTML-документ готовий (промальований)
$(document).ready(function () {
    // Беремо в змінну елемент розмітки з id jq-notification для сповіщень від ajax
    var successMessage = $("#jq-notification");

    // Ловимо подію кліку по кнопці "додати в корзину"
    $(document).on("click", ".add-to-cart", function (e) {
        // Блокуємо її базову дію
        e.preventDefault();

        // Беремо елемент лічильника у значку корзини та беремо звідти значення
        var carsInCartCount = $("#cars-in-cart-count");
        var cartCount = parseInt(carsInCartCount.text() || 0);

        // Отримуємо id авто з атрибута data-car-id
        var car_id = $(this).data("car-id");

        // З атрибута href беремо посилання на контролер django
        var add_to_cart_url = $(this).attr("href");

        // Виконуємо POST-запит через ajax без перезавантаження сторінки
        $.ajax({
            type: "POST",
            url: add_to_cart_url,
            data: {
                car_id: car_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Повідомлення
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7 сек ховаємо повідомлення
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);

                // Збільшуємо кількість авто у корзині (в шаблоні)
                cartCount++;
                carsInCartCount.text(cartCount);

                // Змінюємо вміст корзини на відповідь від django (новий відмальований фрагмент корзини)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },
            error: function (data) {
                console.log("Помилка при додаванні авто в корзину");
            },
        });
    });

    // Ловимо подію кліку по кнопці "видалити авто з корзини"
    $(document).on("click", ".remove-from-cart", function (e) {
        // Блокуємо її базову дію
        e.preventDefault();

        // Беремо елемент лічильника у значку корзини та беремо звідти значення
        var carsInCartCount = $("#cars-in-cart-count");
        var cartCount = parseInt(carsInCartCount.text() || 0);

        // Отримуємо id корзини з атрибута data-cart-id
        var cart_id = $(this).data("cart-id");
        // З атрибута href беремо посилання на контролер django
        var remove_from_cart = $(this).attr("href");

        // Виконуємо POST-запит через ajax без перезавантаження сторінки
        $.ajax({
            type: "POST",
            url: remove_from_cart,
            data: {
                cart_id: cart_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Повідомлення
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7 сек ховаємо повідомлення
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);

                // Зменшуємо кількість авто у корзині (в шаблоні)
                cartCount -= data.period_deleted;
                carsInCartCount.text(cartCount);

                // Змінюємо вміст корзини на відповідь від django (новий відмальований фрагмент корзини)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },
            error: function (data) {
                console.log("Помилка при видаленні авто з корзини");
            },
        });
    });

    // Обробник події для зменшення кількості
    $(document).on("click", ".decrement", function () {
        // Беремо посилання на контролер django з атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Беремо id корзини з атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Шукаємо найближчий input з кількістю
        var $input = $(this).closest('.input-group').find('.number');
        // Отримуємо значення кількості авто
        var currentValue = parseInt($input.val());
        // Якщо кількість більше одного — тільки тоді зменшуємо
        if (currentValue > 1) {
            $input.val(currentValue - 1);
            // Запускаємо функцію, визначену нижче
            updateCart(cartID, currentValue - 1, -1, url);
        }
    });

    $(document).on("keyup", "input.number", function () {
        var url = $(this).data("cart-change-url");
        var cartID = $(this).data("cart-id");
        var $input = $(this).closest('.input-group').find('.number');
        var val = parseInt($input.val());

        // Забезпечуємо мінімальне значення 1
        if (isNaN(val) || val < 1) val = 1;

        // Оновлюємо поле, щоб користувач бачив мінімальне значення
        $input.val(val);

        // Виклик функції для оновлення кошика
        updateCart(cartID, val, 1, url);
    });


    // Обробник події для збільшення кількості
    $(document).on("click", ".increment", function () {
        var url = $(this).data("cart-change-url");
        var cartID = $(this).data("cart-id");
        var $input = $(this).closest('.input-group').find('.number');
        var currentValue = parseInt($input.val());

        $input.val(currentValue + 1);

        updateCart(cartID, currentValue + 1, 1, url);
    });

    function updateCart(cartID, period, change, url) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                cart_id: cartID,
                period: period,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);

                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);
            },
            error: function (data) {
                console.log("Помилка при оновленні кількості авто в корзині");
            },
        });
    }

    // Беремо елемент для сповіщень від django
    var notification = $('#notification');
    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');
        }, 7000);
    }

    // При кліку по значку корзини відкриваємо модальне вікно
    $('#modalButton').click(function () {
        $('#exampleModal').appendTo('body');
        $('#exampleModal').modal('show');
    });

    // Подія кліку по кнопці закриття вікна корзини
    $('#exampleModal .btn-close').click(function () {
        $('#exampleModal').modal('hide');
    });

    // Обробник події для вибору способу доставки
    $("input[name='requires_delivery']").change(function () {
        var selectedValue = $(this).val();
        // Показуємо або приховуємо поле введення адреси доставки
        if (selectedValue === "1") {
            $("#deliveryAddressField").show();
        } else {
            $("#deliveryAddressField").hide();
        }
    });

    // Форматування вводу номера телефону у формі (xxx) xxx-хххх
    document.getElementById('id_phone_number').addEventListener('input', function (e) {
        var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
        e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
    });

    // Перевірка на клієнті правильності номера телефону у формі
    $('#create_order_form').on('submit', function (event) {
        var phoneNumber = $('#id_phone_number').val();
        var regex = /^\(\d{3}\) \d{3}-\d{4}$/;

        if (!regex.test(phoneNumber)) {
            $('#phone_number_error').show();
            event.preventDefault();
        } else {
            $('#phone_number_error').hide();
            var cleanedPhoneNumber = phoneNumber.replace(/[()\-\s]/g, '');
            $('#id_phone_number').val(cleanedPhoneNumber);
        }
    });
});
