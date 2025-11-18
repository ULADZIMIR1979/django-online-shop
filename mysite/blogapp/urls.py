from django.urls import path
from .views import (
    ArticlesListView,
    ArticleDetailView,
    ArticleEditView,
    ArticleCreateView,
    AuthorDetailView,
    LatestArticlesFeed,
)

app_name = 'blogapp'

urlpatterns = [
    path('', ArticlesListView.as_view(), name='article_list_root'),
    path('articles/', ArticlesListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/edit/', ArticleEditView.as_view(), name='article_edit'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/latest/feed/', LatestArticlesFeed(), name='articles_feed'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
]