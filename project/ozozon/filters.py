from django_filters import FilterSet
from .models import Product

class ProductFilter(FilterSet):
   class Meta:
       model = Product
       fields = {
           # поиск по названию
           'product_name': ['icontains'],
           # 'quantity': ['gt'],
           # 'price': [
           #     'lt',  # цена должна быть меньше или равна указанной
           #     'gt',  # цена должна быть больше или равна указанной
           # ],
       }

