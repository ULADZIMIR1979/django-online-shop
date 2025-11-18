# 🛍️ Django Интернет-Магазин

![Django](https://img.shields.io/badge/Django-5.2.6-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-red)
![Status](https://img.shields.io/badge/Status-Завершен-success)

Полнофункциональный интернет-магазин на Django с блогом, REST API и системой аутентификации. Учебный проект для портфолио.

## ✨ Возможности

### 🛒 Магазин
- **Управление товарами** - добавление, редактирование, архивирование
- **Система заказов** - создание и отслеживание заказов
- **Корзина покупок** - добавление/удаление товаров
- **Скидки и акции** - система скидок на товары
- **Категории товаров** - удобная навигация

### 📝 Блог
- **Публикация статей** - CRUD операции для статей
- **Система авторов** - профили авторов с биографией
- **Категории и теги** - организация контента
- **Поиск и фильтрация** - по авторам, категориям, тегам

### 🔐 Безопасность
- **Аутентификация** - регистрация, вход, выход
- **Профили пользователей** - аватарки, личная информация
- **Разграничение прав** - разные уровни доступа
- **Защита CSRF** - встроенная защита Django

### 📱 API
- **RESTful API** - полное API для всех моделей
- **Документация Swagger** - автоматическая генерация docs
- **Фильтрация и поиск** - мощная система фильтров
- **Пагинация** - оптимальная загрузка данных

### 🎨 Администрирование
- **Админ-панель Django** - полное управление данными
- **Кастомные действия** - массовые операции
- **Визуализация данных** - графики и статистика
- **Экспорт данных** - в JSON, CSV форматах

## 🛠 Технологический стек

- **Backend**: Django 5.2.6, Django REST Framework
- **Database**: SQLite3 (разработка), PostgreSQL (продакшен)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **API Documentation**: DRF Spectacular (OpenAPI 3)
- **Monitoring**: Sentry для отслеживания ошибок
- **Debugging**: Django Debug Toolbar
- **Internationalization**: Django i18n (русский/английский)
- **Containerization**: Docker, Docker Compose

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.11+
- pip (менеджер пакетов Python)
- Git

### Установка и запуск

1. **Клонирование репозитория**

```bash
  git clone https://gitlab.skillbox.ru/uladzimir_leshankou/python_django.git
  cd python_django
```


2. **Создание виртуального окружения**

```bash
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    # или
    venv\Scripts\activate     # Windows
```


3. **Установка зависимостей**

```bash
  pip install -r requirements.txt
```


4. **Настройка базы данных**

```bash
    cd mysite
    python manage.py migrate
```


5. **Создание суперпользователя**

```bash
  python manage.py createsuperuser
```


6. **Загрузка тестовых данных (опционально)**

```bash
  python manage.py loaddata shopapp-products-fixtures.json
```


7. **Запуск сервера разработки**

```bash
    python manage.py runserver
```


📁 Структура проекта
```text
python_django/
├── mysite/                 # Корневая директория Django
│   ├── mysite/            # Настройки проекта
│   │   ├── settings.py    # Конфигурация
│   │   ├── urls.py        # Главные URL-ы
│   │   └── wsgi.py        # WSGI конфигурация
│   ├── shopapp/           # Приложение магазина
│   │   ├── models.py      # Модели товаров, заказов
│   │   ├── views.py       # Представления магазина
│   │   ├── admin.py       # Админ-панель
│   │   └── urls.py        # URL-ы магазина
│   ├── blogapp/           # Приложение блога
│   │   ├── models.py      # Модели статей, авторов
│   │   ├── views.py       # Представления блога
│   │   └── management/    # Кастомные команды
│   ├── myauth/            # Аутентификация
│   │   ├── models.py      # Модели пользователей
│   │   └── views.py       # Логика аутентификации
│   ├── myapiapp/          # REST API
│   │   ├── serializers.py # Сериализаторы
│   │   └── views.py       # API представления
│   └── requestdataapp/    # Обработка запросов
├── requirements.txt       # Зависимости Python
├── .gitignore            # Игнорируемые файлы Git
└── README.md             # Документация
```


🌐 Доступные эндпоинты

## Веб-интерфейс

- Главная страница: http://127.0.0.1:8000/

- Магазин: http://127.0.0.1:8000/shop/

- Блог: http://127.0.0.1:8000/blog/

- Аутентификация: http://127.0.0.1:8000/accounts/

## Администрирование

- Админ-панель: http://127.0.0.1:8000/admin/

- Документация админа: http://127.0.0.1:8000/admin/doc/

## API Endpoints

- API Root: http://127.0.0.1:8000/api/

- Swagger UI: http://127.0.0.1:8000/api/schema/swagger/

- ReDoc: http://127.0.0.1:8000/api/schema/redoc/

- Товары API: http://127.0.0.1:8000/api/products/

- Заказы API: http://127.0.0.1:8000/api/orders/

🗄 Модели данных

## Магазин (shopapp)

- Product - Товары (название, описание, цена, скидка)

- Order - Заказы (пользователь, товары, адрес доставки)

- ProductImage - Изображения товаров

## Блог (blogapp)

- Article - Статьи (заголовок, содержание, автор, категория)

- Author - Авторы (имя, биография)

- Category - Категории статей

- Tag - Теги для статей

## Пользователи (myauth)

- Profile - Профили пользователей (аватар, био)

🔧 Кастомные команды

```bash
# Создание тестовых товаров
python manage.py create_products --clear

# Создание тестовых статей для блога
python manage.py create_blog_data --clear

# Экспорт заказов
python manage.py export_orders
```


⚙️ Настройка окружения

Создайте файл .env в директории mysite/:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_DEBUG=True
```


🐳 Запуск через Docker

```bash
# Сборка и запуск
docker-compose up --build

# Остановка
docker-compose down
```

🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Тесты конкретного приложения
python manage.py test shopapp
python manage.py test blogapp

# С покрытием кода
coverage run manage.py test
coverage report
```

📊 Особенности реализации

## Безопасность

- Защита от CSRF атак

- Валидация данных форм

- SQL-инъекции предотвращены ORM

- Безопасная обработка файлов


## Производительность

- Кэширование запросов

- Оптимизированные SQL-запросы

- Пагинация больших наборов данных

- Оптимальная загрузка связанных объектов


## Масштабируемость

- Модульная архитектура

- Микросервисная готовность

- Поддержка нескольких БД

- Контейнеризация через Docker


🤝 Вклад в проект

1. Форкните репозиторий

2. Создайте feature ветку (git checkout -b feature/AmazingFeature)

3. Закоммитьте изменения (git commit -m 'Add some AmazingFeature')

4. Запушьте ветку (git push origin feature/AmazingFeature)

5. Откройте Pull Request


📄 Лицензия

Этот проект создан для учебных целей. Распространяется по лицензии MIT.


👨‍💻 Автор
## Владимир Лешанков

- GitLab: @uladzimir_leshankou

- Email: uladzimir.leshankou@example.com
- 

🙏 Благодарности

- Команда Skillbox за качественное обучение

- Сообщество Django за отличную документацию

- Разработчикам Django REST Framework

⭐ Если этот проект был полезен, поставьте звезду на GitLab!