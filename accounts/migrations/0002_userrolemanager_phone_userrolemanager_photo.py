# Generated by Django 5.0 on 2024-04-13 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrolemanager',
            name='phone',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='userrolemanager',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='user_profile'),
        ),
    ]
