# Generated by Django 3.2.6 on 2021-08-23 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_alter_listing_watchlist_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('EL', 'Electronics'), ('PT', 'Pets'), ('HS', 'Household'), ('MS', 'Miscellaneous')], default='MS', max_length=2),
        ),
    ]
