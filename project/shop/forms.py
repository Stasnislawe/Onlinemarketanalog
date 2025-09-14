from django import forms


class ProductFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-time_create', 'Новинки'),
        ('price', 'Цена по возрастанию'),
        ('-price', 'Цена по убыванию'),
        ('-views', 'По популярности'),
        ('-discount_percent', 'По размеру скидки'),
    ]

    in_stock = forms.BooleanField(
        required=False,
        label='В наличии',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=False
    )

    with_discount = forms.BooleanField(
        required=False,
        label='Со скидкой',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=False
    )

    min_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'От',
            'min': '0'
        })
    )

    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'До',
            'min': '0'
        })
    )

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )