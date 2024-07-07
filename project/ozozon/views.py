from allauth.account import app_settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, TemplateView, DeleteView
from django.contrib.auth.decorators import login_required
from .filters import ProductFilter
from .forms import ProductForm, SignupRegForm, FullProductForm
from .models import Product, Author, ProductImages, Cart
from django.shortcuts import render
from django.http import HttpResponseRedirect



class ProductsListView(ListView):
    model = Product
    ordering = 'product_name'
    template_name = 'ProductsList.html'
    ordering = '-time_create'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'Product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['all_img'] = ProductImages.objects.all().filter(product_id=self.object.pk)
        return context


class ProductCreate(LoginRequiredMixin ,CreateView):
    form_class = FullProductForm
    model = Product
    template_name = 'ProductCreate.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        files = form.cleaned_data["images"]
        for f in files:
            pr = ProductImages(product=Product.objects.get(pk=self.object.pk), images=f)
            pr.save()
        return super().form_valid(form)


class RegisterView(FormView):
    form_class = SignupRegForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy("profile")


class ProfileView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'profile.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        kwargs['my_listproducts'] = Product.objects.filter(author=self.request.user).order_by('-id')
        return super().get_context_data(**kwargs)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = FullProductForm
    template_name = 'ProductUpdate.html'

    def get_context_data(self,**kwargs):
        kwargs['update'] = True
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        files = form.cleaned_data["images"]
        for f in files:
            pr = ProductImages(product=Product.objects.get(pk=self.object.pk), images=f)
            pr.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user != kwargs['instance'].author:
            return self.handle_no_permission()
        return kwargs


@login_required()
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(product=product,
                                                       author=request.user)
    if product.quantity != 0:
        cart_item.quantity += 1
        product.quantity -= 1
        product.save()
        cart_item.save()
        current_page = request.META.get('HTTP_REFERER')
        return redirect(current_page)

    else:
        raise ValueError("Нет в наличие")


def remove_from_cart(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id)
    product = Product.objects.get(id=cart_item.product_id)

    if cart_item.quantity == 1:
        product.quantity += 1
        product.save()
        cart_item.delete()
    else:
        cart_item.quantity -= 1
        product.quantity += 1
        product.save()
        cart_item.save()
    current_page = request.META.get('HTTP_REFERER')
    return redirect(current_page)


class CartView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'mycart.html'
    context_object_name = 'cart'


    def get_context_data(self, **kwargs):
        kwargs['mycart'] = Cart.objects.filter(author=self.request.user).order_by('-product__price')
        cart_items = Cart.objects.filter(author=self.request.user)
        price = (item.product.price * item.quantity for item in cart_items)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        kwargs['total_price'] = total_price
        kwargs['pricequant'] = price
        return super().get_context_data(**kwargs)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.author:
            return self.handle_no_permission()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class ConfirmUser(UpdateView):
    model = Author
    context_object_name = 'confirm_user'

    def post(self, request, *args, **kwargs):
        if 'code' in request.POST:
            user = Author.objects.filter(code=request.POST['code'])
            if user.exists():
                user.update(is_active=True)
                user.update(code=None)
            else:
                return render(self.request, 'registration/invalid_code.html')
        return redirect('account_login')


class AccountInactiveView(TemplateView):
    template_name = "account/account_inactive." + app_settings.TEMPLATE_EXTENSION


account_inactive = AccountInactiveView.as_view()


