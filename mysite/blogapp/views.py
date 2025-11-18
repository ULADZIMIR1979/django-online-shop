from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.contrib import messages

from .models import Article, Author
from .forms import ArticleEditForm, ArticleCreateForm


class ArticlesListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = Article.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).defer(
            'content'
        ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ПРОСТАЯ ПРОВЕРКА - если пользователь аутентифицирован, показываем кнопку
        context['can_create_article'] = self.request.user.is_authenticated

        # ОТЛАДКА в консоль
        print(f"=== DEBUG: User {self.request.user} can_create: {context['can_create_article']} ===")

        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blogapp/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        queryset = Article.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ПРОСТАЯ ПРОВЕРКА - если пользователь аутентифицирован, показываем кнопки
        context['can_edit'] = self.request.user.is_authenticated
        context['can_delete'] = self.request.user.is_authenticated

        # ОТЛАДКА в консоль
        print(f"=== DEBUG: User {self.request.user} can_edit: {context['can_edit']} ===")

        return context

class ArticleEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleEditForm
    template_name = 'blogapp/article_edit.html'
    context_object_name = 'article'

    def test_func(self):
        return self.request.user.has_perm('blogapp.change_article')

    def get_success_url(self):
        messages.success(self.request, 'Статья успешно обновлена!')
        return reverse('blogapp:article_detail', kwargs={'pk': self.object.pk})

class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Article
    form_class = ArticleCreateForm
    template_name = 'blogapp/article_create.html'

    def test_func(self):
        return self.request.user.has_perm('blogapp.add_article')

    def form_valid(self, form):
        # Для простоты берем первого автора или создаем дефолтного
        author, created = Author.objects.get_or_create(
            name='Администратор',
            defaults={'bio': 'Главный администратор блога'}
        )
        form.instance.author = author
        messages.success(self.request, 'Статья успешно создана!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blogapp:article_detail', kwargs={'pk': self.object.pk})

class AuthorDetailView(DetailView):
    model = Author
    template_name = 'blogapp/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(
            author=self.object
        ).select_related('category').prefetch_related('tags').defer('content')
        return context

# Остальной код без изменений
from django.contrib.syndication.views import Feed

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
