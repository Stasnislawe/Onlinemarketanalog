from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from .models import Product, Category
from .forms import ProductFilterForm


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