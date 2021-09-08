"""
python manage.py makemigrations
python manage.py migrate
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post = models.CharField(max_length=280)

    def __str__(self) -> str:
        return f'Post {self.id} by {self.poster}'

class Like(models.Model):
    pass

class Follower(models.Model):
    pass