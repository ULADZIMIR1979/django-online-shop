from django.contrib import admin
from .models import Author, Category, Tag, Article

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'bio_short']
    search_fields = ['name']

    def bio_short(self, obj):
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio

    bio_short.short_description = 'Биография'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'pub_date', 'is_recent']
    list_filter = ['category', 'tags', 'pub_date']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    date_hierarchy = 'pub_date'
    readonly_fields = ['pub_date']

    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'author', 'category', 'tags']
        }),
        ('Содержание', {
            'fields': ['content'],
            'classes': ['wide']
        }),
    ]

    def is_recent(self, obj):
        from django.utils import timezone
        return obj.pub_date >= timezone.now() - timezone.timedelta(days=7)

    is_recent.boolean = True
    is_recent.short_description = 'Новая статья'
    