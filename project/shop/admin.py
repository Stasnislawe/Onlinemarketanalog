from django.contrib import admin
from .models import Cart, Category, Product, ProductImages, Author


admin.site.register(Author)
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImages)

