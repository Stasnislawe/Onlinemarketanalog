from datetime import date

from allauth.account.forms import SignupForm
from django import forms
from string import hexdigits
import random
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
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

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].label = 'Наименование'
        self.fields['discription'].label = 'Содержание'
        self.fields['category'].label = 'Категория'
        self.fields['image'].label = 'Изображение'
        self.fields['quantity'].label = 'Количество'
        self.fields['price'].label = 'Цена'

    class Meta:
        model = Product
        fields = ['product_name',
                  'discription',
                  'price',
                  'image',
                  'quantity',
                  'category',
                  ]




    def clean(self):
        cleaned_data=super().clean()
        name = cleaned_data.get('product_name')
        description = cleaned_data.get('discription')
        price = cleaned_data.get('price')
        quantity = cleaned_data.get('quantity')
        author = cleaned_data.get('author')

        if name is not None and len(name) > 50:
            raise ValidationError({
                "title": "Заголовок не может быть более 50 символов."
            })
        if name == description:
            raise ValidationError(
                "Заголовок не должен быть идентичным тексту статьи.")
        if name[0].islower():
            raise ValidationError(
                "Заголовок должен начинаться с заглавной буквы.")
        if description[0].islower():
            raise ValidationError(
                "Текст статьи должен начинаться с заглавной буквы.")

        today = date.today()
        post_limit = Product.objects.filter(author=author, time_create__date=today).count()
        if post_limit >= 3:
            raise ValidationError({
                'text': "Вы можете публиковать только 3 поста в день!"
            })

        return cleaned_data


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


