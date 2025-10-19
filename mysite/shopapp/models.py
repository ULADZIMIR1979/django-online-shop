from django.contrib.auth.models import User
from django.db import models

def product_preview_directory_path(instance: 'Product', filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    class Meta:
        ordering = ['name']
        permissions = [
            ("can_create_product", "Can create product"),
            ("can_change_product", "Can change product"),
        ]

    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)
    created_by = models.ForeignKey(  # Добавляем связь с пользователем
        User,
        on_delete=models.SET_NULL,
        null=True,  # Временно, для существующих записей
        blank=True,
        related_name='products'
    )

    def __str__(self)->str:
        return f"Product(pk={self.pk}, name={self.name!r})"


def product_images_directory_path(instance: 'ProductImage', filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, blank=True, null=False)


class Order(models.Model):
    class Meta:
        ordering = ['-created_at']
    delivery_address = models.TextField(null=False, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders',)
    archived = models.BooleanField(default=False)
    receipt = models.FileField(null=True, upload_to='orders/receipts/',)

    def __str__(self)->str:
        if self.pk:
            return f"Order(pk={self.pk}, user={self.user.username!r})"
        else:
            return f"Order(user={self.user.username!r})"

    def get_total_price(self):
        return sum(product.price for product in self.products.all())

    def __str__(self):
        return f"Order #{self.pk}"
