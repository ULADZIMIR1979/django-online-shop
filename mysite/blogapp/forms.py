from django import forms
from .models import Article, Author

class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
            'category': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
        }

class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
            'category': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 15px;'}),
        }