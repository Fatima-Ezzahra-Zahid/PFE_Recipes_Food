# Generated by Django 5.1.1 on 2024-09-12 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0002_user_role_alter_user_username'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='dish',
            name='price',
        ),
    ]
