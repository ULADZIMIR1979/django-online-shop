from timeit import default_timer

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

def shop_index(request: HttpRequest):
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

