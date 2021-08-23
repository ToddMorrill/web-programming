"""
python manage.py makemigrations
python manage.py migrate
"""
import json

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass

class Listing(models.Model):
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(0)])
    image_url = models.URLField()
    category = models.CharField(max_length=256)
    # if a winner is set, the auction is closed
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids_won', null=True, blank=True)
    watchlist_users = models.ManyToManyField(User, related_name='watchlist_listings')

    def __str__(self) -> str:
        return f'{self.title}'

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    price = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        return f'Bid by {self.bidder} on {self.listing} for {self.price}'

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()

    def __str__(self) -> str:
        return f'Comment {self.id} on {self.listing} by {self.commenter}'

# class Watchlist(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
#     listings = models.ManyToManyField(Listing, related_name='watchlist_users')

#     def __str__(self) -> str:
#         return f'Watchlist for user {self.user}'