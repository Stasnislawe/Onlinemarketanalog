from django.contrib import admin
from .models import Cart, Product, ProductImages, Author
from .forms import ProductForm
# Register your models here.

class ProductImagesAdmin(admin.ModelAdmin):
  pass


class ProductImagesInline(admin.StackedInline):
  model = ProductImages
  max_num = 10
  extra = 0


class ProductAdmin(admin.ModelAdmin):
  inlines = [ProductImagesInline,]
  form = ProductForm

admin.site.register(ProductImages, ProductImagesAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Author)