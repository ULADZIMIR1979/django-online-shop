from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product


def save_csv_products(file, encoding):
    """Сохраняет товары из CSV-файла в базу данных."""

    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products
