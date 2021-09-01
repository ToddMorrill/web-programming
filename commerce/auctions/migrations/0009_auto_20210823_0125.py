# Generated by Django 3.2.6 on 2021-08-23 01:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_rename_listing_watchlist_listings'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='watchlist_users',
            field=models.ManyToManyField(related_name='watchlist_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Watchlist',
        ),
    ]