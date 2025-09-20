from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Create order")
        user = User.objects.get(username="admin_Vladimir")
        order = Order.objects.get_or_create(
            delivery_address="Москва, ул. Ленина, д. 1",
            promocode="123456",
            user=user,
        )
        self.stdout.write(f"Order created: {order}")