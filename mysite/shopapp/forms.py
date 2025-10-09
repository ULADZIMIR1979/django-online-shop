from django import forms
from django.core import validators
from django.contrib.auth.models import Group
from django.forms import ModelForm

from .models import Product, Order


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "name",


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["delivery_address", "promocode", "user", "products"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].widget = forms.CheckboxSelectMultiple()
        self.fields['products'].queryset = Product.objects.filter(archived=False)