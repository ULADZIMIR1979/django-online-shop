"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""

from timeit import default_timer
import json
import os
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import Group
from django.http import (
    HttpResponse, HttpRequest,
    HttpResponseRedirect, JsonResponse
)
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView, DetailView,
    CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin
)
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущности товара.
    """

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

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, return 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                description="Empty response, product by id not found"
            ),
        }
    )
    def retrieve(self, *args, **kwargs):
        """Retrieve a product instance."""
        return super().retrieve(*args, **kwargs)


@extend_schema(description="Order views CRUD")
class OrderViewSet(ModelViewSet):
    """
    Набор представлений для действий над Order.

    Полный CRUD для сущности заказа.
    """

    queryset = Order.objects.select_related(
        'user'
    ).prefetch_related('products').all()
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

    @extend_schema(
        summary="Get one order by ID",
        description="Retrieves **order** with details, "
                    "return 404 if not found",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(
                description="Empty response, order by id not found"
            ),
        }
    )
    def retrieve(self, *args, **kwargs):
        """Retrieve an order instance."""
        return super().retrieve(*args, **kwargs)


class ShopIndexView(View):
    """View for shop index page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET request for shop index."""
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
    """View for groups list page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET request for groups list."""
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        """Handle POST request for groups list."""
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    """View for product details page."""

    template_name = 'shopapp/product-details.html'
    queryset = Product.objects.prefetch_related("images")
    context_object_name = 'product'


class ProductsListView(ListView):
    """View for products list page."""

    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """View for creating a product."""

    permission_required = 'shopapp.add_product'
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        """Validate form and set created_by user."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    """View for updating a product."""

    model = Product
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def test_func(self):
        """Test if user has permission to update product."""
        product = self.get_object()
        if self.request.user.is_superuser:
            return True
        return (
            self.request.user.has_perm('shopapp.change_product') and
            product.created_by == self.request.user
        )

    def get_success_url(self):
        """Get success URL after update."""
        return reverse(
            'shopapp:product_details',
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        """Validate form and handle product images."""
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    """View for deleting a product."""

    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        """Archive product instead of deleting."""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    """View for orders list page."""

    template_name = 'shopapp/order-list.html'
    model = Order
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related("products")
        .filter(archived=False)
    )


class OrderDetailsView(LoginRequiredMixin, DetailView):
    """View for order details page."""

    template_name = 'shopapp/order_detail.html'
    model = Order
    context_object_name = 'order'

    def get_object(self, queryset=None):
        """Get order object with access control."""
        order = super().get_object(queryset)
        self.access_denied = not (
            self.request.user.is_superuser or order.user == self.request.user
        )
        if self.access_denied:
            return order
        return order

    def get_context_data(self, **kwargs):
        """Add access_denied flag to context."""
        context = super().get_context_data(**kwargs)
        context['access_denied'] = getattr(self, 'access_denied', False)
        return context


class OrderCreateView(CreateView):
    """View for creating an order."""

    model = Order
    form_class = OrderForm
    template_name = 'shopapp/order_form.html'
    success_url = reverse_lazy('shopapp:order_list')


class OrderUpdateView(UpdateView):
    """View for updating an order."""

    model = Order
    form_class = OrderForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        """Get success URL after update."""
        return reverse(
            'shopapp:order_details',
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    """View for deleting an order."""

    model = Order
    success_url = reverse_lazy('shopapp:order_list')

    def form_valid(self, form):
        """Archive order instead of deleting."""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductsDataExportView(View):
    """View for exporting products data as JSON."""

    def get(self, request: HttpRequest) -> JsonResponse:
        """Export products data as JSON."""
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
    """Главная страница экспорта заказов с кнопками."""

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        """Check if user is staff before dispatching."""
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET request for orders export page."""
        orders_count = Order.objects.count()
        context = {
            'orders_count': orders_count,
        }
        return render(request, 'shopapp/orders_export.html', context=context)


class OrdersExportJSONView(View):
    """Возвращает JSON данных заказов в браузере."""

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        """Check if user is staff before dispatching."""
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest) -> JsonResponse:
        """Export orders data as JSON in browser."""
        orders = Order.objects.select_related(
            'user'
        ).prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": {
                    "id": order.user.pk if order.user else None,
                    "username": order.user.username if order.user else None,
                },
                "products": [
                    {
                        "id": product.pk,
                        "name": product.name,
                        "price": str(product.price),
                    }
                    for product in order.products.all()
                ],
                "archived": order.archived,
            })

        return JsonResponse({"orders": orders_data})


class OrdersExportDownloadView(View):
    """Скачивание JSON файла с данными заказов."""

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        """Check if user is staff before dispatching."""
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        """Download orders data as JSON file."""
        orders = Order.objects.select_related(
            'user'
        ).prefetch_related('products').all()

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

        export_dir = os.path.join(settings.BASE_DIR, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        timestamp = now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_export_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            with open(filepath, 'rb') as f:
                response = HttpResponse(
                    f.read(), content_type='application/json'
                )
                response['Content-Disposition'] = (
                    f'attachment; filename="{filename}"'
                )
                return response

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка при сохранении файла: {str(e)}"
            }, status=500)
