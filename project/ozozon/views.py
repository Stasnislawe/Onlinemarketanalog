from allauth.account import app_settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, TemplateView, DeleteView

from .filters import ProductFilter
from .forms import ProductForm, SignupRegForm, FullProductForm
from .models import Product, Author, ProductImages
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


class ProductCreate(CreateView):
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


