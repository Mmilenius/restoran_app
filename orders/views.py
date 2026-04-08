from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin # Додано
import json

from carts.views import CartService
from .models import Order, OrderItem
from .forms import OrderForm

# Додаємо LoginRequiredMixin — тепер тільки залогінені бачать цю сторінку
class CreateOrderView(LoginRequiredMixin, View):
    # Куди відправити аноніма (AllAuth стандарт)
    login_url = 'account_login'

    def get(self, request):
        cart_service = CartService(request)
        cart_summary = cart_service.get_cart_summary()

        if cart_summary['total_items'] == 0:
            messages.warning(request, 'Ваша корзина порожня')
            return redirect('restaurant:menu')

        form = OrderForm()
        return render(request, 'orders/create_order.html', {
            'form': form,
            'cart_summary': cart_summary
        })

    @transaction.atomic
    def post(self, request):
        # Цей метод можна залишити для звичайних форм,
        # але оскільки ти використовуєш AJAX (CreateOrderAPIView),
        # основна логіка тепер там.
        pass


class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        # Додаємо перевірку, щоб користувач міг бачити ТІЛЬКИ СВОЄ успішне замовлення
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, 'orders/order_success.html', {
            'order': order
        })


class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        # Тепер ми впевнені, що користувач авторизований завдяки LoginRequiredMixin
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/order_list.html', {
            'orders': orders
        })


@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderAPIView(View):
    # Тут не ставимо міксин, а перевіряємо всередині, щоб повернути гарний JSON
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Ви повинні увійти в систему'
            }, status=401)

        try:
            data = json.loads(request.body)
            table_number = int(data.get('table_number'))
            notes = data.get('notes', '')

            cart_service = CartService(request)
            cart_summary = cart_service.get_cart_summary()

            if cart_summary['total_items'] == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Корзина порожня'
                })

            with transaction.atomic():
                # Створюємо замовлення ТУТ ДОДАНО user=request.user
                order = Order.objects.create(
                    cart=cart_summary['cart'],
                    user=request.user, # ОБОВ'ЯЗКОВО ДЛЯ ПРОФІЛЮ
                    table_number=table_number,
                    total_price=cart_summary['total_price'],
                    notes=notes
                )

                # Створюємо позиції замовлення
                for cart_item in cart_summary['items']:
                    OrderItem.objects.create(
                        order=order,
                        dish_name=cart_item.dish.name,
                        dish_price=cart_item.dish.price,
                        quantity=cart_item.quantity,
                        total_price=cart_item.get_total_price()
                    )

                # Очищаємо корзину
                cart_service.clear_cart()

            return JsonResponse({
                'success': True,
                'message': f'Замовлення #{order.id} створено успішно',
                'order_id': order.id,
                'redirect_url': f'/orders/success/{order.id}/'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка: {str(e)}'
            })