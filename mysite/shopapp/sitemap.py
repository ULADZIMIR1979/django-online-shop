from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Order


class ProductSitemap(Sitemap):
    """Sitemap для товаров."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(archived=False)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('shopapp:product_details', kwargs={'pk': obj.pk})


class OrderSitemap(Sitemap):
    """Sitemap для заказов."""

    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Order.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('shopapp:order_details', kwargs={'pk': obj.pk})


class ShopStaticSitemap(Sitemap):
    """Sitemap для статических страниц."""

    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ['shopapp:products_list', 'shopapp:orders_list']

    def location(self, item):
        return reverse(item)


class ShopSitemap(Sitemap):
    """Sitemap для всего приложения shopapp."""

    changefreq = "weekly"
    priority = 0.7

    def items(self):
        # Возвращаем все продукты и заказы
        products = Product.objects.filter(archived=False)
        orders = Order.objects.all()
        return list(products) + list(orders)

    def lastmod(self, obj):
        if hasattr(obj, 'created_at'):
            return obj.created_at
        return None

    def location(self, obj):
        if isinstance(obj, Product):
            return reverse('shopapp:product_details', kwargs={'pk': obj.pk})
        elif isinstance(obj, Order):
            return reverse('shopapp:order_details', kwargs={'pk': obj.pk})