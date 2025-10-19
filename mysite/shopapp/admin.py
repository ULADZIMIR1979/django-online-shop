from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInLine(admin.StackedInline):
    model = ProductImage


@admin.action(description="Mark selected products as archived")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Mark selected products as unarchived")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInLine,
    ]
    list_display = "pk", "name", "description_shot", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "name", "pk"
    list_filter = "name",
    search_fields = "name", "description", "price", "discount", "created_at"
    fieldsets = [
        (None, {
            'fields': ("name", "description"),
        }),
        ("Price options", {
            'fields': ("price", "discount"),
            'classes': ("wide", "collapse"),
        }),
        ("Images", {
            'fields': ("preview",),
        }),
        ("Extra options", {
            'fields': ("archived",),
            'classes': ("collapse"),
            'description': "Extra options. Field 'archived' is soft delete.",
        }),
    ]


    def description_shot(self, obj: Product)->str:
        if len(obj.description) < 50:
            return obj.description
        return obj.description[:50] + "..."


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order)->str:
        return obj.user.first_name or obj.user.username



