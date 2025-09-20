from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

from carts.views import CartService
from .models import Order, OrderItem
from .forms import OrderForm


class CreateOrderView(View):
    def get(self, request):
        cart_service = CartService(request)
        cart_summary = cart_service.get_cart_summary()

        if cart_summary['total_items'] == 0:
            messages.warning(request, 'Ваша корзина порожня')
            return redirect('dish:menu')

        form = OrderForm()
        return render(request, 'orders/create_order.html', {
            'form': form,
            'cart_summary': cart_summary
        })

    @transaction.atomic
    def post(self, request):
        cart_service = CartService(request)
        cart_summary = cart_service.get_cart_summary()

        if cart_summary['total_items'] == 0:
            messages.warning(request, 'Ваша корзина порожня')
            return redirect('dish:menu')

        form = OrderForm(request.POST)

        if form.is_valid():
            try:
                # Створюємо замовлення
                order = Order.objects.create(
                    cart=cart_summary['cart'],
                    user=request.user if request.user.is_authenticated else None,
                    table_number=form.cleaned_data['table_number'],
                    total_price=cart_summary['total_price'],
                    notes=form.cleaned_data['notes']
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

                messages.success(request,
                                 f'Замовлення #{order.id} успішно створено! Очікуйте на столику {order.table_number}')
                return redirect('orders:order_success', order_id=order.id)

            except Exception as e:
                messages.error(request, f'Помилка при створенні замовлення: {str(e)}')
                return redirect('orders:create_order')

        return render(request, 'orders/create_order.html', {
            'form': form,
            'cart_summary': cart_summary
        })


class OrderSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/order_success.html', {
            'order': order
        })


class OrderListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
        else:
            # Для неавторизованих користувачів - пустий список
            orders = Order.objects.none()

        return render(request, 'orders/order_list.html', {
            'orders': orders
        })


@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderAPIView(View):
    def post(self, request):
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

            # Створюємо замовлення
            order = Order.objects.create(
                cart=cart_summary['cart'],
                user=request.user if request.user.is_authenticated else None,
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
