from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductDetailsView,
    ProductsListView,
    OrdersListView,
    OrderDetailsView,
    ProductCreateView,
    ProductUpdateView,
    OrderCreateView,
    OrderUpdateView,
    ProductDeleteView,
    OrderDeleteView,
    ProductsDataExportView,
    OrdersExportView,
    OrdersExportJSONView,
    OrdersExportDownloadView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed, UserOrdersExportView, UserOrdersListView,
)

app_name = 'shopapp'

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),

    path('api/', include(router.urls)),

    path('groups/', GroupsListView.as_view(), name='groups_list'),

path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', UserOrdersExportView.as_view(), name='user_orders_export'),

    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/export/', ProductsDataExportView.as_view(), name='products_export'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/latest/feed/', LatestProductsFeed(), name='product_feed'),

    path('orders/', OrdersListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='create_order'),
    path('orders/<int:pk>/', OrderDetailsView.as_view(), name='order_details'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/archive/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/export/', OrdersExportView.as_view(), name='orders_export'),
    path('orders/export/json/', OrdersExportJSONView.as_view(), name='orders_export_json'),
    path('orders/export/download/', OrdersExportDownloadView.as_view(), name='orders_export_download'),
]