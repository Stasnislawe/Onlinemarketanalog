from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import categorylist

class Author(AbstractUser):
    code = models.CharField(max_length=15, blank=True, null=True)


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    discription = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(default='Цена не указана')
    quantity = models.IntegerField(default=1)
    images = models.ImageField(upload_to="photos/%Y/%m/%d/", default='photos/nophoto.jpg', verbose_name="Фото")
    category = models.CharField(max_length=7, choices=categorylist)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product_name}: {self.discription}: {self.price}'

class Cart(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def summma(self):
        product_price = self.product.price
        return self.quantity * product_price







