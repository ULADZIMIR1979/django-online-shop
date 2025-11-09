from django.views.generic import ListView, DetailView
from .models import Article, Author


class ArticlesListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        # Оптимизация запросов для решения проблемы N+1
        queryset = Article.objects.select_related(
            'author',  # ForeignKey - используем select_related
            'category'  # ForeignKey - используем select_related
        ).prefetch_related(
            'tags'  # ManyToManyField - используем prefetch_related
        ).defer(
            'content'  # Исключаем поле content, так как оно не используется в шаблоне
        ).order_by('-pub_date')

        return queryset


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blogapp/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        # Для детальной страницы ЗАГРУЖАЕМ content
        queryset = Article.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        )
        return queryset


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'blogapp/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем статьи автора в контекст
        context['articles'] = Article.objects.filter(
            author=self.object
        ).select_related('category').prefetch_related('tags').defer('content')
        return context
