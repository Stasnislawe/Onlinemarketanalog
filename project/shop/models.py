# shop/models.py
from django.db import models
from django.conf import settings  # используем settings.AUTH_USER_MODEL
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание категории')
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name='Изображение категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category_products', kwargs={'category_slug': self.slug})

    def get_product_count(self):
        return self.products.count()


def get_product_image_filename(instance, filename):
    prdname = instance.product_name
    slug = slugify(prdname)
    return f"product_images/{slug}-{filename}"


def get_additional_image_filename(instance, filename):
    prdname = instance.product.product_name
    slug = slugify(prdname)
    return f"product_images/additional/{slug}-{filename}"


class Product(models.Model):
    product_name = models.CharField(max_length=50, verbose_name='Наименование')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL')
    description = models.TextField(verbose_name="Описание")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=get_product_image_filename, default='photos/nophoto.jpg',
                              verbose_name="Основное Фото")
    price = models.PositiveIntegerField(verbose_name='Цена', validators=[MinValueValidator(1)])
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество', validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f'{self.product_name}'

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'product_slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to=get_additional_image_filename, verbose_name="Дополнительное фото")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Дополнительное фото'
        verbose_name_plural = 'Дополнительные фото'
        ordering = ['-created_at']


class Cart(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = ['author', 'product']

    def __str__(self):
        return f'{self.author.email} - {self.product.product_name}'

    def get_total_price(self):
        return self.product.price * self.quantity