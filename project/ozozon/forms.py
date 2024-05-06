from allauth.account.forms import SignupForm
from django import forms
from string import hexdigits
import random

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from .models import Product, Author


class SignupRegForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Author

class RegistrationForm(SignupForm):

    def save(self, request):
        user = super(RegistrationForm, self).save(request)
        user.is_active = False
        code = ''.join(random.sample(hexdigits, 5))
        user.code = code
        user.save()
        send_mail(
            subject=f'Код активации',
            message=f'Код активации {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        return user


class ProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].label = 'Название'
        self.fields['discription'].label = 'Описание'
        self.fields['price'].label = 'Цена'
        self.fields['quantity'].label = 'Количество'
        self.fields['category'].label = 'Категория'
        self.fields['images'].label = 'Изображения'

    class Meta:
        model = Product

        fields = ['product_name',
                  'discription',
                  'price',
                  'quantity',
                  'category',
                  'images']