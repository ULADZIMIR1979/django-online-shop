from django.db import models
from django.contrib.auth.models import User

def avatar_upload_path(instance, filename):
    # instance - это экземпляр Profile
    # filename - оригинальное имя файла
    user_pk = instance.user.pk
    return f'avatars/user_{user_pk}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

