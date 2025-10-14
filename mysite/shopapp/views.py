from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order


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
    model = Product
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


# class ProductCreateView(UserPassesTestMixin, CreateView):
#     def test_func(self):
#         return self.request.user.is_superuser
#     model = Product
#     fields = "name", "price", "description", "discount"
#     success_url = reverse_lazy('shopapp:products_list')

class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'shopapp.add_product'
    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        # Связываем продукт с текущим пользователем
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = '_update_form'

    def test_func(self):
        """Проверяем может ли пользователь редактировать продукт"""
        product = self.get_object()

        # Суперпользователь может редактировать всегда
        if self.request.user.is_superuser:
            return True

        # Обычный пользователь может редактировать только свои продукты
        # и если у него есть разрешение на изменение
        return (
                self.request.user.has_perm('shopapp.change_product') and
                product.created_by == self.request.user
        )

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={"pk": self.object.pk},
        )


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


# class OrderDetailsView(PermissionRequiredMixin, DetailView):
#     permission_required = 'shopapp.view_order'
#     template_name = 'shopapp/order_detail.html'
#     model = Order
#     context_object_name = 'order'
#     queryset = (
#         Order.objects.select_related('user').prefetch_related("products")
#     )

class OrderDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'shopapp/order_detail.html'
    model = Order
    context_object_name = 'order'

    def get_object(self, queryset=None):
        order = super().get_object(queryset)

        # Сохраняем информацию о доступе
        self.access_denied = not (self.request.user.is_superuser or order.user == self.request.user)

        if self.access_denied:
            # Все равно возвращаем объект, но в шаблоне проверим access_denied
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


