from allauth.account.forms import SignupForm
from django import forms
from string import hexdigits
import random

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from .models import Product, Author, ProductImages


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

    class Meta:
        model = Product
        fields = ['product_name',
                  'discription',
                  'price',
                  'image',
                  'quantity',
                  'category',
                  ]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class FullProductForm(ProductForm):
    images = MultipleFileField()

    class Meta(ProductForm.Meta):
        fields = ProductForm.Meta.fields + ['images', ]


