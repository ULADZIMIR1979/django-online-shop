from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles'
    )

    def get_absolute_url(self):
        return reverse("blogapp:article_detail", kwargs={"pk": self.pk})

    def can_edit(self, user):
        """Проверка, может ли пользователь редактировать статью"""
        return user.is_authenticated and user.has_perm('blogapp.change_article')

    def can_delete(self, user):
        """Проверка, может ли пользователь удалять статью"""
        return user.is_authenticated and user.has_perm('blogapp.delete_article')

    def __str__(self):
        return self.title


