# Generated by Django 5.1.1 on 2024-09-25 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0013_remove_contact_phone_numer_contact_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
