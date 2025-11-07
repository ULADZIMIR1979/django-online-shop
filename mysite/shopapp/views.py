from timeit import default_timer
import json
import os
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.select_related('user').prefetch_related('products').all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "user",
        "products",
        "archived",
    ]
    ordering_fields = [
        "pk",
        "delivery_address",
        "created_at",
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            {"name": "Laptop", "price": 1999},
            {"name": "Desktop", "price": 2999},
            {"name": "Smartphone", "price": 999},
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'shopapp.add_product'
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def test_func(self):
        product = self.get_object()
        if self.request.user.is_superuser:
            return True
        return (
                self.request.user.has_perm('shopapp.change_product') and
                product.created_by == self.request.user
        )

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/order-list.html'
    model = Order
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related("products")
        .filter(archived=False)
    )


class OrderDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'shopapp/order_detail.html'
    model = Order
    context_object_name = 'order'

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        self.access_denied = not (self.request.user.is_superuser or order.user == self.request.user)
        if self.access_denied:
            return order
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['access_denied'] = getattr(self, 'access_denied', False)
        return context


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'shopapp/order_form.html'
    success_url = reverse_lazy('shopapp:order_list')


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:order_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})


class OrdersExportView(View):
    """Главная страница экспорта заказов с кнопками"""

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        # Получаем количество заказов для отображения в шаблоне
        orders_count = Order.objects.count()

        context = {
            'orders_count': orders_count,
        }
        return render(request, 'shopapp/orders_export.html', context=context)


class OrdersExportJSONView(View):
    """Возвращает JSON данных заказов в браузере"""

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.select_related('user').prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.pk,  # ИЗМЕНЕНО: 'id' вместо 'pk'
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": {  # ИЗМЕНЕНО: объект user вместо user_id
                    "id": order.user.pk if order.user else None,
                    "username": order.user.username if order.user else None,
                },
                "products": [  # ИЗМЕНЕНО: массив объектов вместо ID
                    {
                        "id": product.pk,
                        "name": product.name,
                        "price": str(product.price),
                    }
                    for product in order.products.all()
                ],
                "archived": order.archived,  # ДОБАВЛЕНО: поле archived
            })

        return JsonResponse({"orders": orders_data})


class OrdersExportDownloadView(View):
    """Скачивание JSON файла с данными заказов"""

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.select_related('user').prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk if order.user else None,
                "products": [product.pk for product in order.products.all()],
            })

        result_data = {"orders": orders_data}

        # Создаем директорию для экспорта если её нет
        export_dir = os.path.join(settings.BASE_DIR, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        # Генерируем имя файла с timestamp
        timestamp = now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_export_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)

        # Сохраняем данные в файл
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            # Возвращаем файл для скачивания
            with open(filepath, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/json')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка при сохранении файла: {str(e)}"
            }, status=500)