from django.core.management.base import BaseCommand
from django.utils import timezone

from blogapp.models import Author, Category, Tag, Article


class Command(BaseCommand):
    help = 'Создает тестовые данные для блога'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед созданием новых',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        self.create_authors()
        self.create_categories()
        self.create_tags()
        self.create_articles()

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы!')
        )

    def clear_data(self):
        """Очистка существующих данных"""
        Article.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()

        self.stdout.write('Существующие данные очищены.')

    def create_authors(self):
        """Создание авторов"""
        authors_data = [
            {
                'name': 'Иван Иванов',
                'bio': 'Опытный разработчик с 5-летним стажем. Специализируется на Python и веб-разработке.'
            },
            {
                'name': 'Мария Петрова',
                'bio': 'Data scientist и ML инженер. Любит исследовать данные и создавать интеллектуальные системы.'
            },
            {
                'name': 'Алексей Сидоров',
                'bio': 'Full-stack разработчик. Работает как с фронтендом, так и с бэкендом.'
            }
        ]

        self.authors = []
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                name=author_data['name'],
                defaults=author_data
            )
            self.authors.append(author)

        self.stdout.write(f'Создано авторов: {len(self.authors)}')

    def create_categories(self):
        """Создание категорий"""
        categories_data = [
            'Программирование',
            'Data Science',
            'Веб-разработка',
            'Базы данных',
            'DevOps'
        ]

        self.categories = []
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(name=category_name)
            self.categories.append(category)

        self.stdout.write(f'Создано категорий: {len(self.categories)}')

    def create_tags(self):
        """Создание тегов"""
        tags_data = [
            'Python', 'Django', 'Web', 'JavaScript', 'React',
            'ML', 'AI', 'SQL', 'Docker', 'Kubernetes',
            'REST', 'API', 'Testing', 'Deployment', 'Tutorial'
        ]

        self.tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            self.tags.append(tag)

        self.stdout.write(f'Создано тегов: {len(self.tags)}')

    def create_articles(self):
        """Создание статей"""
        articles_data = [
            {
                'title': 'Основы Django: создание первого приложения',
                'content': '''В этой статье мы рассмотрим основы Django и создадим простое веб-приложение.

Django - это высокоуровневый Python веб-фреймворк, который позволяет быстро создавать безопасные и поддерживаемые веб-сайты. 

Основные преимущества Django:
• Быстрая разработка
• Высокая безопасность
• Масштабируемость
• Отличная документация

Для начала работы установите Django:
pip install django

Создайте новый проект:
django-admin startproject myproject

Запустите сервер разработки:
python manage.py runserver

Теперь ваш сайт доступен по адресу http://127.0.0.1:8000/

Django следует архитектуре MVT (Model-View-Template), которая очень похожа на MVC. Это позволяет четко разделять логику приложения, данные и представление.''',
                'author': self.authors[0],
                'category': self.categories[0],
                'tags': ['Python', 'Django', 'Tutorial']
            },
            {
                'title': 'Машинное обучение для начинающих',
                'content': '''Введение в машинное обучение: от линейной регрессии до нейронных сетей.

Машинное обучение (Machine Learning) - это подраздел искусственного интеллекта, который позволяет компьютерам обучаться на данных без явного программирования.

Основные типы машинного обучения:

1. Обучение с учителем (Supervised Learning)
   - Классификация
   - Регрессия

2. Обучение без учителя (Unsupervised Learning)
   - Кластеризация
   - Понижение размерности

3. Обучение с подкреплением (Reinforcement Learning)

Популярные библиотеки для ML в Python:
• Scikit-learn - для классических алгоритмов ML
• TensorFlow и PyTorch - для глубокого обучения
• Pandas и NumPy - для работы с данными

Пример простой линейной регрессии:

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)''',
                'author': self.authors[1],
                'category': self.categories[1],
                'tags': ['Python', 'ML', 'AI', 'Tutorial']
            },
            {
                'title': 'Современная веб-разработка с React и Django',
                'content': '''Как создать SPA приложение с React на фронтенде и Django на бэкенде.

В современной веб-разработке часто используется подход, когда бэкенд (Django) предоставляет API, а фронтенд (React) отвечает за пользовательский интерфейс.

Архитектура приложения:

Бэкенд (Django):
• Django REST Framework для создания API
• Модели для работы с базой данных
• Сериализаторы для преобразования данных
• Представления (Views) для обработки запросов

Фронтенд (React):
• Компоненты для UI
• Состояние (State) для управления данными
• HTTP-запросы к API
• Маршрутизация (React Router)

Преимущества такого подхода:
• Разделение ответственности
• Возможность использовать разные технологии
• Легкость масштабирования
• Удобство тестирования

Пример Django View с DRF:

from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

Пример React компонента:

import React, { useState, useEffect } from 'react';

function ArticleList() {
    const [articles, setArticles] = useState([]);

    useEffect(() => {
        fetch('/api/articles/')
            .then(response => response.json())
            .then(data => setArticles(data));
    }, []);

    return (
        <div>
            {articles.map(article => (
                <div key={article.id}>
                    <h3>{article.title}</h3>
                    <p>{article.content}</p>
                </div>
            ))}
        </div>
    );
}''',
                'author': self.authors[2],
                'category': self.categories[2],
                'tags': ['Python', 'Django', 'React', 'JavaScript', 'Web']
            },
            {
                'title': 'Оптимизация запросов в Django ORM',
                'content': '''Изучаем методы select_related, prefetch_related и другие способы оптимизации запросов к базе данных.

Проблема N+1 запросов - одна из самых распространенных проблем в веб-приложениях. Она возникает когда для каждой основной записи делается дополнительный запрос к связанным данным.

Решение проблемы:

1. select_related() - для ForeignKey и OneToOneField
   Выполняет SQL JOIN и загружает связанные объекты в одном запросе.

   Пример:
   articles = Article.objects.select_related('author', 'category')

2. prefetch_related() - для ManyToManyField и обратных связей
   Выполняет отдельный запрос для каждой связи, но оптимизирует загрузку.

   Пример:
   articles = Article.objects.prefetch_related('tags')

3. only() и defer() - для выбора конкретных полей
   only() - загружает только указанные поля
   defer() - исключает указанные поля из запроса

   Пример:
   articles = Article.objects.only('title', 'pub_date')
   articles = Article.objects.defer('content')

4. values() и values_list() - для получения словарей или кортежей
   Уменьшает объем данных и время выполнения.

   Пример:
   articles = Article.objects.values('title', 'author__name')

Правильная оптимизация может ускорить приложение в десятки раз! Всегда проверяйте количество запросов с помощью Django Debug Toolbar.''',
                'author': self.authors[0],
                'category': self.categories[0],
                'tags': ['Python', 'Django', 'SQL', 'Testing']
            },
            {
                'title': 'Docker для Django разработчиков',
                'content': '''Полное руководство по контейнеризации Django приложений с помощью Docker.

Docker позволяет упаковать приложение со всеми зависимостями в контейнер, который может работать на любой системе.

Основные преимущества Docker:
• Изоляция окружения
• Простота развертывания
• Масштабируемость
• Совместимость между средами

Структура Docker-проекта для Django:

myproject/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── myapp/
    └── ...

Пример Dockerfile для Django:

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

Пример docker-compose.yml:

version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydatabase
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword

Запуск приложения:
docker-compose up --build

Docker значительно упрощает процесс разработки и деплоя Django приложений!''',
                'author': self.authors[2],
                'category': self.categories[4],
                'tags': ['Docker', 'Deployment', 'DevOps']
            }
        ]

        created_count = 0
        for i, article_data in enumerate(articles_data):
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'content': article_data['content'],
                    'pub_date': timezone.now(),
                    'author': article_data['author'],
                    'category': article_data['category']
                }
            )

            if created:
                # Добавляем теги к статье
                tag_names = article_data['tags']
                tags_to_add = [tag for tag in self.tags if tag.name in tag_names]
                article.tags.set(tags_to_add)
                created_count += 1

        self.stdout.write(f'Создано статей: {created_count}')