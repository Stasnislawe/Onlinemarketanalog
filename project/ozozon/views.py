from allauth.account import app_settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, TemplateView
from .forms import ProductForm, SignupRegForm
from .models import Product, Author


class ProductsListView(ListView):
    model = Product
    ordering = 'product_name'
    template_name = 'ProductsList.html'
    context_object_name = 'products'


class ProductDetail(DetailView):
    model = Product
    template_name = 'Product.html'
    context_object_name = 'product'


class ProductCreate(CreateView):
    form_class = ProductForm
    model = Product
    template_name = 'ProductCreate.html'
    success_url = reverse_lazy('plist')

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class RegisterView(FormView):
    form_class = SignupRegForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy("profile")


@login_required
def profile_view(request):
    return render(request, 'profile.html')


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


