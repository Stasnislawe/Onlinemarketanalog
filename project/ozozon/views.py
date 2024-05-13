from allauth.account import app_settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, TemplateView, DeleteView
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



class ProfileView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'profile.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        kwargs['my_listproducts'] = Product.objects.filter(author=self.request.user).order_by('-id')
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


