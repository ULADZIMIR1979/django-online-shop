from random import choices
from string import ascii_letters

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers

import json


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):

    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            is_staff=True,
        )

        # ДОБАВЛЯЕМ КОНКРЕТНОЕ РАЗРЕШЕНИЕ
        add_product_permission = Permission.objects.get(codename='add_product')
        self.user.user_permissions.add(add_product_permission)

        self.client.login(username='testuser', password='testpassword123')

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "10000",
                "description": "A good table",
                "discount": "10",
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product.objects.create(
            name="Test Product",
            price=1000,
            description="Test Description",
            discount=5
        )

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        super().tearDownClass()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        # проверки
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpassword123")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertEqual(response.status_code, 302, )
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_export_products_view(self):
        response = self.client.get(
            reverse("shopapp:products_export"),
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        )
        # Добавляем разрешение на просмотр заказа
        view_order_permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(view_order_permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        # Вход пользователя
        self.client.force_login(self.user)
        # Создаем заказ для теста
        self.order = Order.objects.create(
            delivery_address="Test Address 123",
            promocode="TEST2024",
            user=self.user
        )

    def tearDown(self):
        # Удаляем заказ после теста
        self.order.delete()

    def test_order_details(self):
        # Выводим информацию о созданном заказе
        print("\n" + "=" * 50)
        print("📦 ИНФОРМАЦИЯ О ТЕСТОВОМ ЗАКАЗЕ:")
        print("=" * 50)
        print(f"ID заказа: {self.order.pk}")
        print(f"Адрес доставки: {self.order.delivery_address}")
        print(f"Промокод: '{self.order.promocode}'")
        print(f"Пользователь: {self.order.user.username}")
        print(f"Продукты в заказе: {list(self.order.products.all())}")
        print("=" * 50)

        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )

        # Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # Выводим информацию о ответе
        print("\n📄 ИНФОРМАЦИЯ О HTML ОТВЕТЕ:")
        print("=" * 50)
        response_content = response.content.decode('utf-8')

        # Ищем адрес доставки в ответе
        if self.order.delivery_address in response_content:
            print(f"✅ Адрес '{self.order.delivery_address}' найден в ответе")
        else:
            print(f"❌ Адрес '{self.order.delivery_address}' НЕ найден в ответе")

        # Ищем промокод в ответе
        if self.order.promocode in response_content:
            print(f"✅ Промокод '{self.order.promocode}' найден в ответе")
        else:
            print(f"❌ Промокод '{self.order.promocode}' НЕ найден в ответе")

        print("=" * 50)

        # Проверяем, что в теле ответа есть адрес заказа
        self.assertContains(response, self.order.delivery_address)

        # Проверяем, что в теле ответа есть промокод
        self.assertContains(response, self.order.promocode)

        # Проверяем, что в контексте тот же заказ
        self.assertEqual(response.context['order'].pk, self.order.pk)

        # Дополнительная проверка данных в контексте
        order_in_context = response.context['order']
        print(f"\n🔍 ПРОВЕРКА КОНТЕКСТА:")
        print(f"ID заказа в контексте: {order_in_context.pk}")
        print(f"ID тестового заказа: {self.order.pk}")
        print(f"Совпадают: {order_in_context.pk == self.order.pk}")
        print("=" * 50)


class OrdersExportTestCase(TestCase):
    fixtures = [
        'groups.json',  # ДОБАВЛЕНО: фикстура групп
        'users.json',
        'products.json',
        'orders.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя с правами staff для тестов
        cls.user = User.objects.create_user(
            username='export_test_user',
            password='testpassword123',
            is_staff=True
        )

    @classmethod
    def tearDownClass(cls):
        # Удаляем только созданного для тестов пользователя
        User.objects.filter(username='export_test_user').delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_export(self):
        """Тест экспорта заказов в JSON"""
        response = self.client.get(reverse('shopapp:orders_export_json'))

        # Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # Проверяем Content-Type
        self.assertEqual(response['Content-Type'], 'application/json')

        # Парсим JSON ответ
        data = response.json()

        # Проверяем структуру ответа
        self.assertIn('orders', data)

        # Получаем заказы из базы для сравнения
        orders_from_db = Order.objects.select_related('user').prefetch_related('products').all()

        # Проверяем количество заказов
        self.assertEqual(len(data['orders']), orders_from_db.count())

        # Проверяем каждый заказ в ответе
        for order_data, order_db in zip(data['orders'], orders_from_db):
            # Проверяем основные поля
            self.assertEqual(order_data['id'], order_db.pk)
            self.assertEqual(order_data['delivery_address'], order_db.delivery_address)
            self.assertEqual(order_data['promocode'], order_db.promocode)
            self.assertEqual(order_data['archived'], order_db.archived)

            # Проверяем пользователя
            self.assertEqual(order_data['user']['id'], order_db.user.pk)
            self.assertEqual(order_data['user']['username'], order_db.user.username)

            # Проверяем продукты
            self.assertEqual(len(order_data['products']), order_db.products.count())

            # Проверяем каждый продукт в заказе
            for product_data, product_db in zip(order_data['products'], order_db.products.all()):
                self.assertEqual(product_data['id'], product_db.pk)
                self.assertEqual(product_data['name'], product_db.name)
                self.assertEqual(str(product_data['price']), str(product_db.price))

    def test_orders_export_requires_staff_permission(self):
        """Тест что обычные пользователи не могут получить доступ"""
        # Создаем обычного пользователя без прав staff
        regular_user = User.objects.create_user(
            username='regular_user',
            password='testpassword123',
            is_staff=False
        )

        self.client.force_login(regular_user)
        response = self.client.get(reverse('shopapp:orders_export_json'))

        # Должны получить отказ в доступе (403) или редирект на логин (302)
        self.assertIn(response.status_code, [403, 302])

        # Убираем пользователя
        regular_user.delete()

    def test_orders_export_json_structure(self):
        """Тест на правильность структуры JSON"""
        response = self.client.get(reverse('shopapp:orders_export_json'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()

        # Проверяем основную структуру
        self.assertIsInstance(data, dict)
        self.assertIn('orders', data)
        self.assertIsInstance(data['orders'], list)

        # Проверяем структуру первого заказа (если есть заказы)
        if data['orders']:
            order = data['orders'][0]
            expected_fields = ['id', 'delivery_address', 'promocode', 'user', 'products', 'archived']

            for field in expected_fields:
                self.assertIn(field, order)

            # Проверяем структуру пользователя
            self.assertIn('id', order['user'])
            self.assertIn('username', order['user'])

            # Проверяем структуру продуктов
            self.assertIsInstance(order['products'], list)
            if order['products']:
                product = order['products'][0]
                product_fields = ['id', 'name', 'price']
                for field in product_fields:
                    self.assertIn(field, product)

    def test_orders_export_has_correct_data_from_fixtures(self):
        """Тест что данные из фикстур корректно экспортируются"""
        response = self.client.get(reverse('shopapp:orders_export_json'))

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Проверяем конкретные данные из фикстур
        orders = data['orders']

        # Должно быть 2 заказа из фикстур
        self.assertEqual(len(orders), 2)

        # Проверяем первый заказ (pk=2 из фикстур)
        order_2 = next((order for order in orders if order['id'] == 2), None)
        self.assertIsNotNone(order_2)
        self.assertEqual(order_2['delivery_address'], "Mogilev")
        self.assertEqual(order_2['promocode'], "")
        self.assertEqual(order_2['user']['id'], 2)  # user admin_Vladimir
        self.assertEqual(order_2['user']['username'], "admin_Vladimir")

        # Проверяем второй заказ (pk=3 из фикстур)
        order_3 = next((order for order in orders if order['id'] == 3), None)
        self.assertIsNotNone(order_3)
        self.assertEqual(order_3['delivery_address'], "Ужгород,90")
        self.assertEqual(order_3['promocode'], "asd")
        self.assertEqual(order_3['user']['id'], 4)  # user Olga
        self.assertEqual(order_3['user']['username'], "Olga")