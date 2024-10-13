# Generated by Django 5.1.1 on 2024-09-24 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0012_rename_subject_contact_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='phone_numer',
        ),
        migrations.AddField(
            model_name='contact',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='contact',
            name='full_name',
            field=models.CharField(max_length=100),
        ),
    ]
