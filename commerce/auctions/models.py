"""
python manage.py makemigrations
python manage.py migrate
"""
import json

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.CharField(max_length=256, blank=True)

    def set_foo(self, x):
        self.watchlist = json.dumps(x)

    def get_watchlist(self):
        return json.loads(self.watchlist)


class Listing(models.Model):
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=11, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=256, blank=True)
    # listing_datetime = models.DateTimeField()


    def __str__(self) -> str:
        return f'{self.title}'


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    price = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f'Bid by {self.bidder} on {self.listing} for {self.price}'

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()

    def __str__(self) -> str:
        return f'Comment {self.id} on {self.listing} by {self.commenter}'