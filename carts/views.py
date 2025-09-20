# carts/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from dish.models import Dish
from .models import Cart, CartItem


class CartService:
    """Сервіс для роботи з корзиною"""

    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self.session = request.session
        if not self.session.session_key:
            self.session.save()

    def get_or_create_cart(self):
        """Отримує або створює корзину"""
        if self.user:
            cart, _ = Cart.objects.get_or_create(user=self.user, defaults={'session_key': None})
        else:
            cart, _ = Cart.objects.get_or_create(session_key=self.session.session_key, user=None)
        return cart

    def add_dish(self, dish_id, quantity=1):
        """Додає страву в корзину"""
        dish = Dish.objects.get(id=dish_id)
        cart = self.get_or_create_cart()
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, dish=dish, defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def update_quantity(self, dish_id, quantity):
        """Оновлює кількість страви"""
        cart = self.get_or_create_cart()
        try:
            cart_item = cart.items.get(dish_id=dish_id)
            if quantity <= 0:
                cart_item.delete()
                return None
            cart_item.quantity = quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return None

    def remove_dish(self, dish_id):
        cart = self.get_or_create_cart()
        try:
            cart_item = cart.items.get(dish_id=dish_id)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def clear_cart(self):
        self.get_or_create_cart().items.all().delete()

    def get_cart_summary(self):
        cart = self.get_or_create_cart()
        items = cart.items.select_related('dish').all()
        total_items = sum(item.quantity for item in items)
        total_price = sum(item.get_total_price() for item in items)
        return {
            'cart': cart,
            'items': items,
            'total_items': total_items,
            'total_price': total_price,
        }


class CartView(View):
    """Відображення корзини (вкладене у шаблоні/модальне вікно)"""
    def get(self, request):
        cart_service = CartService(request)
        cart_summary = cart_service.get_cart_summary()
        return render(request, 'carts/cart.html', {
            'cart_items': cart_summary['items'],
            'total_items': cart_summary['total_items'],
            'total_price': cart_summary['total_price'],
        })


@method_decorator(csrf_exempt, name='dispatch')
class AddToCartView(View):
    def post(self, request):
        data = json.loads(request.body)
        dish_id = int(data.get('dish_id'))
        quantity = int(data.get('quantity', 1))
        cart_service = CartService(request)
        cart_item = cart_service.add_dish(dish_id, quantity)
        cart_summary = cart_service.get_cart_summary()
        return JsonResponse({
            'success': True,
            'message': f'Страву "{cart_item.dish.name}" додано до корзини',
            'cart_total_items': cart_summary['total_items'],
            'cart_total_price': float(cart_summary['total_price']),
            'item': {
                'id': cart_item.id,
                'dish_id': cart_item.dish.id,
                'dish_name': cart_item.dish.name,
                'dish_price': float(cart_item.dish.price),
                'quantity': cart_item.quantity,
                'total_price': float(cart_item.get_total_price()),
                'dish_image': cart_item.dish.image.url if cart_item.dish.image else None
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class UpdateCartView(View):
    def post(self, request):
        data = json.loads(request.body)
        dish_id = int(data.get('dish_id'))
        quantity = int(data.get('quantity'))
        cart_service = CartService(request)
        cart_item = cart_service.update_quantity(dish_id, quantity)
        cart_summary = cart_service.get_cart_summary()

        return JsonResponse({
            'success': True,
            'message': 'Кількість оновлено' if quantity > 0 else 'Товар видалено',
            'cart_total_items': cart_summary['total_items'],
            'cart_total_price': float(cart_summary['total_price']),
            'item_total_price': float(cart_item.get_total_price()) if cart_item else 0
        })


@method_decorator(csrf_exempt, name='dispatch')
class RemoveFromCartView(View):
    def post(self, request):
        data = json.loads(request.body)
        dish_id = int(data.get('dish_id'))
        cart_service = CartService(request)
        success = cart_service.remove_dish(dish_id)
        cart_summary = cart_service.get_cart_summary()
        return JsonResponse({
            'success': success,
            'message': 'Товар видалено з корзини' if success else 'Не знайдено',
            'cart_total_items': cart_summary['total_items'],
            'cart_total_price': float(cart_summary['total_price'])
        })


@method_decorator(csrf_exempt, name='dispatch')
class ClearCartView(View):
    def post(self, request):
        cart_service = CartService(request)
        cart_service.clear_cart()
        return JsonResponse({'success': True, 'message': 'Корзину очищено'})
