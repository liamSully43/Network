# Generated by Django 3.2.7 on 2021-11-08 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0011_auto_20211108_1907'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserFollowers',
            new_name='UserFollower',
        ),
    ]
