"""
Модели для приложения интернет-магазина.

Содержит модели Product, ProductImage и Order.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


def product_preview_directory_path(instance: 'Product', filename: str) -> str:
    """Генерирует путь к директории для изображения
    предварительного просмотра товара."""

    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель Product представляет товар.

    Товар, который можно продавать в интернет-магазине.

    Заказы тут: :model:`shopapp.Order`
    """

    class Meta:
        """Мета-опции для модели Product."""

        ordering = ['name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        permissions = [
            ("can_create_product", "Can create product"),
            ("can_change_product", "Can change product"),
        ]

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(
        null=True, blank=True, upload_to=product_preview_directory_path
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    def __str__(self) -> str:
        """Возвращает строковое представление модели Product."""

        return f"Product(pk={self.pk}, name={self.name!r})"


def product_images_directory_path(instance: 'ProductImage', filename: str) -> str:
    """Генерирует путь к директории для изображения товара."""

    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )

def get_absolute_url(self):
    """Возвращает URL-адрес страницы с деталями товара."""

    return reverse('shopapp:product_details', kwargs={'pk': self.pk})


class ProductImage(models.Model):
    """Модель ProductImage представляет изображение товара."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, blank=True, null=False)


class Order(models.Model):
    """Модель Order представляет заказ пользователя."""

    class Meta:
        """Мета-опции для модели Order."""

        ordering = ['-created_at']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    delivery_address = models.TextField(null=False, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')
    archived = models.BooleanField(default=False)
    receipt = models.FileField(null=True, upload_to='orders/receipts/')

    def __str__(self) -> str:
        """Возвращает строковое представление модели Order."""

        if self.pk:
            return f"Order(pk={self.pk}, user={self.user.username!r})"
        else:
            return f"Order(user={self.user.username!r})"

    def get_total_price(self):
        """Возвращает общую стоимость заказа."""

        return sum(product.price for product in self.products.all())
