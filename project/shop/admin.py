from django.contrib import admin
from .models import Category, Product, ProductImages


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImages)

