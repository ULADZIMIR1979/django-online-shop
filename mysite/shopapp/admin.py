import csv
import json

from django.contrib import admin
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm, OrderImportForm


class OrderInline(admin.TabularInline):
    """Встраиваемая модель для отображения связанных продуктов."""

    model = Product.orders.through


class ProductInLine(admin.StackedInline):
    """Встраиваемая модель для отображения связанных продуктов."""

    model = ProductImage


@admin.action(description="Mark selected products as archived")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Mark selected products as unarchived")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    """Админ-панель для модели Product."""

    change_list_template = 'shopapp/products_changelist.html'
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

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            file=form.files['csv_file'].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data from CSV file was imported.")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-products-csv/',
                self.import_csv,
                name='import_products_csv',
            ),
        ]
        return new_urls + urls


class ProductInline(admin.StackedInline):
    """Встраиваемая модель для отображения связанных продуктов."""

    model = Order.products.through


# В admin.py обновите класс OrderAdmin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админ-панель для модели Order."""

    change_list_template = 'shopapp/orders_changelist.html'
    inlines = [
        ProductInline,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-orders/',
                self.import_orders,
                name='import_orders',
            ),
        ]
        return new_urls + urls

    def import_orders(self, request: HttpRequest) -> HttpResponse:
        """Обработка импорта заказов."""
        if request.method == "GET":
            form = OrderImportForm()
            context = {
                'form': form,
                'title': 'Импорт заказов',
            }
            return render(request, 'admin/csv_form.html', context)

        form = OrderImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
                'title': 'Импорт заказов',
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        try:
            file = form.files['file']
            file_format = form.cleaned_data['file_format']

            if file_format == 'auto':
                # Автоопределение формата по расширению
                file_extension = file.name.split('.')[-1].lower()
                if file_extension == 'csv':
                    orders_created = self.import_from_csv(file)
                elif file_extension == 'json':
                    orders_created = self.import_from_json(file)
                else:
                    messages.error(request, "Неподдерживаемый формат файла")
                    return redirect("..")
            elif file_format == 'csv':
                orders_created = self.import_from_csv(file)
            elif file_format == 'json':
                orders_created = self.import_from_json(file)
            else:
                messages.error(request, "Неподдерживаемый формат файла")
                return redirect("..")

            messages.success(request, f"Успешно создано {orders_created} заказов")
            return redirect("..")

        except Exception as e:
            messages.error(request, f"Ошибка при импорте: {str(e)}")
            return redirect("..")

    def import_from_csv(self, file):
        """Импорт заказов из CSV файла."""
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        orders_created = 0

        for row in reader:
            try:
                # Получаем пользователя
                user = None
                if row.get('user_id'):
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user = User.objects.get(pk=int(row['user_id']))
                    except (ValueError, User.DoesNotExist):
                        print(f"Пользователь с ID {row['user_id']} не найден")
                        continue

                # Создание заказа
                order = Order.objects.create(
                    delivery_address=row.get('delivery_address', ''),
                    promocode=row.get('promocode', ''),
                    user=user,
                )

                # Добавление товаров к заказу
                product_ids = row.get('products', '')
                if product_ids:
                    try:
                        product_ids = [int(pid.strip()) for pid in product_ids.split(',') if pid.strip()]
                        products = Product.objects.filter(pk__in=product_ids, archived=False)
                        order.products.set(products)
                    except (ValueError, TypeError) as e:
                        print(f"Ошибка при обработке товаров: {e}")

                orders_created += 1
                print(f"Создан заказ #{order.pk}")

            except Exception as e:
                print(f"Ошибка при создании заказа: {e}")
                continue

        return orders_created

    def import_from_json(self, file):
        """Импорт заказов из JSON файла."""
        file_content = file.read().decode('utf-8')
        data = json.loads(file_content)
        orders_created = 0

        for order_data in data.get('orders', []):
            try:
                # Получаем пользователя
                user = None
                user_id = order_data.get('user_id')
                if user_id:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user = User.objects.get(pk=int(user_id))
                    except (ValueError, User.DoesNotExist):
                        print(f"Пользователь с ID {user_id} не найден")
                        continue

                # Создание заказа
                order = Order.objects.create(
                    delivery_address=order_data.get('delivery_address', ''),
                    promocode=order_data.get('promocode', ''),
                    user=user,
                )

                # Добавление товаров к заказу
                product_ids = order_data.get('products', [])
                if product_ids:
                    products = Product.objects.filter(pk__in=product_ids, archived=False)
                    order.products.set(products)

                orders_created += 1
                print(f"Создан заказ #{order.pk}")

            except Exception as e:
                print(f"Ошибка при создании заказа: {e}")
                continue

        return orders_created



