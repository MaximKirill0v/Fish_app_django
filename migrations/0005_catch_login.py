# Generated by Django 4.2.4 on 2023-10-12 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Fish_app_django', '0004_remove_catch_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='catch',
            name='login',
            field=models.CharField(default='User', max_length=100),
        ),
    ]
