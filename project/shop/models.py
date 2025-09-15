from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model  # добавляем импорт

User = get_user_model()


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
        return reverse('category_products', kwargs={'category_slug': self.slug})

    def get_product_count(self):
        return self.products.count()


def get_image_filename(instance, filename):
    # Для модели Product
    if hasattr(instance, 'product_name'):
        prdname = instance.product_name
        slug = slugify(prdname)
        return f"product_images/{slug}-{filename}"

    # Для модели ProductImages
    elif hasattr(instance, 'product'):
        prdname = instance.product.product_name
        slug = slugify(prdname)
        return f"product_images/additional/{slug}-{filename}"

    # Запасной вариант
    else:
        return f"product_images/unknown-{filename}"


class Product(models.Model):
    product_name = models.CharField(max_length=50, verbose_name='Наименование')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL')
    description = models.TextField(verbose_name="Описание")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=get_image_filename, default='photos/nophoto.jpg',
                              verbose_name="Основное Фото")
    price = models.PositiveIntegerField(verbose_name='Цена', validators=[MinValueValidator(1)])
    old_price = models.PositiveIntegerField(verbose_name='Старая цена', blank=True, null=True)
    discount_percent = models.PositiveIntegerField(verbose_name='Скидка %', default=0,
                                                   validators=[MinValueValidator(0), MaxValueValidator(100)])
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество', validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
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
            models.Index(fields=['discount_percent']),  # Добавляем индекс для скидок
        ]

    def __str__(self):
        return f'{self.product_name}'

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        # Сохраняем оригинальную цену как old_price при первой установке скидки
        if self.discount_percent > 0:
            if not self.old_price:
                # Если старая цена не установлена, сохраняем текущую цену как старую
                self.old_price = self.price
                # Пересчитываем новую цену
                self.price = int(self.old_price * (100 - self.discount_percent) / 100)
            elif self.old_price and self._state.adding:
                # Если товар новый и есть старая цена, пересчитываем
                self.price = int(self.old_price * (100 - self.discount_percent) / 100)
        elif self.discount_percent == 0 and self.old_price:
            # Если скидку убрали, восстанавливаем оригинальную цену
            self.price = self.old_price
            self.old_price = None

        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        return self.discount_percent > 0

    @property
    def discount_amount(self):
        if self.has_discount and self.old_price:
            return self.old_price - self.price
        return 0


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to=get_image_filename, verbose_name="Дополнительное фото")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Дополнительное фото'
        verbose_name_plural = 'Дополнительные фото'
        ordering = ['-created_at']


class Cart(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = ['author', 'product']

    def __str__(self):
        return f'{self.author.username} - {self.product.product_name}'

    def get_total_price(self):
        return self.product.price * self.quantity