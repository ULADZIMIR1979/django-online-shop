from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

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


class LatestArticlesFeed(Feed):
    title = "Последние статьи блога"
    link = "/blog/articles/"
    description = "Новые статьи из нашего блога"

    def items(self):
        return Article.objects.order_by('-pub_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:200] + "..." if len(item.content) > 200 else item.content

    def item_link(self, item: Article):
        return reverse('blogapp:article_detail', args=[item.pk])

    def item_pubdate(self, item):
        return item.pub_date
