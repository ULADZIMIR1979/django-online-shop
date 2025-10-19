from django import forms
from django.core import validators
from django.contrib.auth.models import Group
from django.forms import ModelForm

from .models import Product, Order, ProductImage


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "name",


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = MultipleImageField(
        required=False,
        label="Additional images"
    )

    def save(self, commit=True):
        product = super().save(commit=commit)

        # Сохраняем дополнительные изображения
        images = self.cleaned_data.get('images', [])
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return product


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["delivery_address", "promocode", "user", "products"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].widget = forms.CheckboxSelectMultiple()
        self.fields['products'].queryset = Product.objects.filter(archived=False)
