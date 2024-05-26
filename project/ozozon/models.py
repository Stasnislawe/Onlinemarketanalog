from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.template.defaultfilters import slugify
from .choices import categorylist

class Author(AbstractUser):
    code = models.CharField(max_length=15, blank=True, null=True)


def get_image_filename(instance, filename):
    prdname = instance.id
    slug = slugify(prdname)
    return "product_images/%s-%s" % (slug, filename)


class Product(models.Model):
    product_name = models.CharField(max_length=50, verbose_name='Наименование')
    discription = models.TextField(verbose_name="Описание")
    time_create = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=get_image_filename, default='photos/nophoto.jpg', verbose_name="Основное Фото")
    price = models.FloatField(default='Цена не указана', verbose_name='Цена')
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    category = models.CharField(max_length=7, choices=categorylist, verbose_name='Категория')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product_name}: {self.discription}: {self.price}'

    def get_absolute_url(self):
        return reverse('detail', args=[str(self.id)])

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images = models.ImageField(upload_to=get_image_filename, default='photos/nophoto.jpg', verbose_name="Дополнительные Фотографии")


class Cart(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def summma(self):
        product_price = self.product.price
        return self.quantity * product_price







