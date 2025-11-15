from django import forms
from django.core import validators
from django.contrib.auth.models import Group
from django.forms import ModelForm

from .models import Product, Order, ProductImage


class GroupForm(forms.ModelForm):
    """Форма для создания и редактирования групп пользователей."""

    class Meta:
        model = Group
        fields = "name",


class MultipleFileInput(forms.ClearableFileInput):
    """Виджет для загрузки нескольких файлов."""

    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Поле для загрузки нескольких изображений."""

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
    """Форма для создания и редактирования товаров."""

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
    """Форма для создания заказа."""

    class Meta:
        model = Order
        fields = ["delivery_address", "promocode", "user", "products"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].widget = forms.CheckboxSelectMultiple()
        self.fields['products'].queryset = Product.objects.filter(archived=False)


class CSVImportForm(forms.Form):
    """Форма для загрузки CSV файла."""

    csv_file = forms.FileField()


class OrderImportForm(forms.Form):
    """Форма для импорта заказов из файла."""

    file = forms.FileField(
        label='Выберите файл для импорта заказов',
        help_text='Поддерживаемые форматы: CSV, JSON'
    )

    file_format = forms.ChoiceField(
        choices=[
            ('auto', 'Автоопределение'),
            ('csv', 'CSV'),
            ('json', 'JSON'),
        ],
        initial='auto',
        label='Формат файла'
    )
