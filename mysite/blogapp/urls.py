from django.urls import path
from .views import (
    ArticlesListView,
    ArticleDetailView,
    AuthorDetailView,
    LatestArticlesFeed,
)

app_name = 'blogapp'

urlpatterns = [
    path('', ArticlesListView.as_view(), name='article_list_root'),
    path('articles/', ArticlesListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/latest/feed/', LatestArticlesFeed(), name='articles_feed'),

    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
]