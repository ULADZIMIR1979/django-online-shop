from django.contrib import admin
from .models import Author, Category, Tag, Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "pub_date")
    list_filter = ("author", "category", "pub_date")
    search_fields = ("title", "content", "author__name")
    filter_horizontal = ("tags",)
    ordering = ("-pub_date",)  # Сортировка по умолчанию: новые сверху

    # Разрешить сортировку по этим полям кликом на заголовок
    sortable_by = ["id", "title", "author", "category", "pub_date"]


# Простые настройки для остальных моделей
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    ordering = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    ordering = ("name",)