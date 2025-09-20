from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Avg
from .models import Category, Dish


# Create your views here.
class CategoryListView(ListView):
    """Список всіх категорій"""
    model = Category
    template_name = 'dish/menu.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True).annotate(
            dishes_count=Count('dishes', filter=Q(dishes__is_available=True))
        )


def menu_view(request):
    """Головна сторінка меню"""
    # Отримуємо всі активні категорії з підрахунком страв
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        dishes_count=Count('dishes', filter=Q(dishes__is_available=True))
    ).prefetch_related('dishes')

    # Популярні страви
    popular_dishes = Dish.objects.filter(
        is_popular=True,
        is_available=True
    ).select_related('category')[:6]

    # Пошук
    search_query = request.GET.get('search', '')
    dishes = None

    # Фільтрація по категорії
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)

    if search_query:
        # Якщо є пошук
        dishes = Dish.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query),
            is_available=True
        ).select_related('category')

        # Якщо також вибрана категорія, додаємо фільтр по категорії
        if selected_category:
            dishes = dishes.filter(category=selected_category)
    elif selected_category:
        # Якщо вибрана категорія без пошуку
        dishes = Dish.objects.filter(
            category=selected_category,
            is_available=True
        ).select_related('category').order_by('name')
    else:
        # Якщо немає ні пошуку, ні фільтра по категорії - показуємо всі страви
        dishes = Dish.objects.filter(
            is_available=True
        ).select_related('category').order_by('category__name', 'name')

    # Додаємо debug інформацію
    print(f"Search query: {search_query}")
    print(f"Selected category: {selected_category}")
    print(f"Total dishes count: {dishes.count() if dishes else 0}")
    print(f"Popular dishes count: {popular_dishes.count()}")

    context = {
        'categories': categories,
        'popular_dishes': popular_dishes,
        'dishes': dishes,
        'search_query': search_query,
        'selected_category': selected_category,
    }

    return render(request, 'dish/menu.html', context)


class DishDetailView(DetailView):
    """Детальна сторінка страви"""
    model = Dish
    template_name = 'dish/dish_detail.html'
    context_object_name = 'dish'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Додаємо схожі страви з тієї ж категорії
        context['similar_dishes'] = Dish.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(id=self.object.id)[:4]
        return context