"""
python manage.py makemigrations
python manage.py migrate
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    poster = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    post = models.CharField(max_length=280)
    created = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField(User, related_name='liked_posts')

    def __str__(self) -> str:
        return f'Post {self.id} by {self.poster}'


class Follower(models.Model):
    followed = models.ForeignKey(User,
                                    on_delete=models.CASCADE,
                                    related_name='followers')
    follower = models.ForeignKey(User,
                                    on_delete=models.CASCADE,
                                    related_name='following')
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('followed', 'follower',)