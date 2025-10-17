from django.test import TestCase, Client
from django.urls import reverse


class GerCookieViewTestsCase(TestCase):

    def setUp(self):
        # Создаем клиент с заголовками по умолчанию
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Test Client)')

    def test_get_cookie_view(self):
        response = self.client.get(reverse("myauth:cookie_get"))
        self.assertContains(response, "Cookie value")


class FooBarViewTest(TestCase):

    def test_foo_bar_view(self):
        response = self.client.get(reverse("myauth:foo-bar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers['content-type'],'application/json'
        )
        expected_data = {"foo": "bar", "spam": "eggs"}
        self.assertJSONEqual(response.content, expected_data)