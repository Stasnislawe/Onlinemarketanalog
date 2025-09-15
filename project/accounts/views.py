from django.views.generic import TemplateView
from django.db.models import Sum
from .models import UserProfile, Order
from .forms import UserProfileForm
from shop.models import Cart
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('shop:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы уже авторизованы.')
            return redirect('shop:home')
        return super().get(request, *args, **kwargs)


class LoginView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('shop:home')

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Добро пожаловать, {user.email}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Неверный email или пароль.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы уже авторизованы.')
            return redirect('shop:home')
        return super().get(request, *args, **kwargs)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('shop:home')


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['profile'] = user.profile
        context['orders'] = Order.objects.filter(user=user).order_by('-created_at')[:10]
        context['cart_items'] = Cart.objects.filter(author=user)
        context['cart_total'] = Cart.objects.filter(author=user).aggregate(
            total=Sum('product__price')
        )['total'] or 0
        context['active_tab'] = self.request.GET.get('tab', 'profile')

        return context


@login_required
def update_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/update_profile.html', {'form': form})