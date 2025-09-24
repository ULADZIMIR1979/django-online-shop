from django.http import HttpRequest, HttpResponse
import time
from datetime import datetime, timedelta


def setup_useragent_on_request_middleware(get_response):
    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print("after get response")
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.request_count += 1
        print("requests count", self.request_count)
        response = self.get_response(request)
        self.responses_count += 1
        print("responses count", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_history = {}  # {ip: [timestamp1, timestamp2, ...]}
        self.max_requests = 3  # максимум 3 запроса
        self.time_window = 5  # за 5 секунд

    def __call__(self, request: HttpRequest):
        ip = self.get_client_ip(request)
        now = time.time()

        # Пропускаем статические файлы
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return self.get_response(request)

        # Инициализируем историю для IP
        if ip not in self.request_history:
            self.request_history[ip] = []

        # Удаляем запросы старше time_window
        self.request_history[ip] = [
            ts for ts in self.request_history[ip]
            if now - ts < self.time_window
        ]

        if len(self.request_history[ip]) > self.max_requests + 1:
            oldest = min(self.request_history[ip])
            wait_time = self.time_window - (now - oldest)
            return HttpResponse(
                f'Слишком много запросов. Лимит: {self.max_requests} запросов в {self.time_window} секунд. '
                f'Подождите {wait_time:.1f} секунд.',
                status=429
            )

        # Добавляем текущий запрос
        self.request_history[ip].append(now)

        # Периодическая очистка
        if now % 10 < 0.1:  # очищаем примерно каждые 10 секунд
            self.cleanup_old_entries()

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def cleanup_old_entries(self):
        """Удаляем записи старше 1 минуты"""
        now = time.time()
        minute_ago = now - 60
        self.request_history = {
            ip: [ts for ts in timestamps if ts > minute_ago]
            for ip, timestamps in self.request_history.items()
            if any(ts > minute_ago for ts in timestamps)
        }
