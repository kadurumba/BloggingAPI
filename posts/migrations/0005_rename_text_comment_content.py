# Generated by Django 4.2.11 on 2024-12-25 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_likedislike_unique_together_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='content',
        ),
    ]
