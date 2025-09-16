from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from .models import Product, Category, Cart
from .forms import ProductFilterForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CategoryContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.annotate(
            product_count=Count('products')
        ).filter(products__is_active=True)
        context['top_categories'] = Category.objects.annotate(
            product_count=Count('products')
        ).filter(products__is_active=True).order_by('-product_count')[:5]
        return context


class HomeView(CategoryContextMixin, ListView):
    model = Product
    template_name = 'shop/home.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'author')

        # Фильтрация по наличию
        in_stock = self.request.GET.get('in_stock')
        if in_stock:
            queryset = queryset.filter(quantity__gt=0)

        # Фильтрация по скидкам
        with_discount = self.request.GET.get('with_discount')
        if with_discount:
            queryset = queryset.filter(discount_percent__gt=0)

        # Фильтрация по цене
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Сортировка
        sort_by = self.request.GET.get('sort_by', '-time_create')
        if sort_by in ['price', '-price', '-time_create', '-views']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ProductFilterForm(self.request.GET or None)
        return context


class ProductDetailView(CategoryContextMixin, DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'product_slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        return context


class CategoryProductsView(CategoryContextMixin, ListView):
    model = Product
    template_name = 'shop/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        queryset = Product.objects.filter(
            category=self.category,
            is_active=True
        ).select_related('category', 'author')

        # Добавляем фильтрацию как в HomeView
        in_stock = self.request.GET.get('in_stock')
        if in_stock:
            queryset = queryset.filter(quantity__gt=0)

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        sort_by = self.request.GET.get('sort_by', '-time_create')
        if sort_by in ['price', '-price', '-time_create', '-views']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['filter_form'] = ProductFilterForm(self.request.GET or None)
        return context


def search_products(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category')
    current_category = None

    # Базовый queryset
    products = Product.objects.filter(is_active=True)

    # Фильтрация по категории если указана
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # Поисковый запрос
    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Дополнительная фильтрация
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(quantity__gt=0)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_by = request.GET.get('sort_by', '-time_create')
    if sort_by in ['price', '-price', '-time_create', '-views']:
        products = products.order_by(sort_by)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'query': query,
        'current_category': current_category,  # Передаем объект категории вместо slug
        'current_category_slug': category_slug,
        'filter_form': ProductFilterForm(request.GET or None),
    }

    return render(request, 'shop/search_results.html', context)


@require_POST
@login_required
def add_to_cart(request, product_id):
    """Универсальное добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id)

    # Получаем количество из POST запроса
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1

    # Проверяем доступное количество
    if quantity > product.quantity:
        quantity = product.quantity
        message = f'Добавлено максимальное доступное количество: {product.quantity}'
    else:
        message = f'Товар добавлен в корзину'

    # Ищем товар в корзине пользователя
    cart_item, created = Cart.objects.get_or_create(
        author=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # Если товар уже есть в корзине, увеличиваем количество
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.quantity:
            new_quantity = product.quantity
            message = f'Установлено максимальное доступное количество: {product.quantity}'

        cart_item.quantity = new_quantity
        cart_item.save()

    # Получаем актуальное количество товаров в корзине
    cart_count = Cart.objects.filter(author=request.user).count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_count,
            'item_quantity': cart_item.quantity,
            'product_quantity': product.quantity
        })
    else:
        messages.success(request, message)
        return redirect('shop:home')


@login_required
def remove_from_cart(request, cart_item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(Cart, id=cart_item_id, author=request.user)
    product_name = cart_item.product.product_name
    cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Товар удален из корзины',
            'cart_count': Cart.objects.filter(author=request.user).count()
        })
    else:
        messages.success(request, f'Товар "{product_name}" удален из корзины')
        return redirect('accounts:profile') + '?tab=cart'


@login_required
def update_cart_quantity(request, cart_item_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_item_id, author=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity,
                'item_total': cart_item.get_total_price(),
                'cart_total': get_cart_total(request.user)
            })
        else:
            # Если количество 0 - удаляем товар
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_count': Cart.objects.filter(author=request.user).count(),
                'cart_total': get_cart_total(request.user)
            })


@login_required
def cart_view(request):
    """Страница корзины"""
    cart_items = Cart.objects.filter(author=request.user).select_related('product')
    total = sum(item.get_total_price() for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# Вспомогательная функция
def get_cart_total(user):
    """Получение общей суммы корзины"""
    cart_items = Cart.objects.filter(author=user)
    return sum(item.get_total_price() for item in cart_items)