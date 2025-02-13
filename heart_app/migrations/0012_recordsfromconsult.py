# Generated by Django 5.0 on 2024-04-13 21:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heart_app', '0011_assigned_test_from_heart_dep'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordsFromConsult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disease', models.CharField(max_length=100)),
                ('date', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='heart_app.patients')),
            ],
        ),
    ]
