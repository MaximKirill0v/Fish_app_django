# Generated by Django 4.2.4 on 2023-10-12 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Fish_app_django', '0003_alter_catch_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='catch',
            name='login',
        ),
    ]
