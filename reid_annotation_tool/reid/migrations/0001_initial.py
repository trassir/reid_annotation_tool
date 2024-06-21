# Generated by Django 5.0.6 on 2024-06-13 22:00

import pgvector.django
from django.db import migrations, models

from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True, verbose_name='Crop ID')),
                ('embedding', pgvector.django.VectorField(dimensions=1024, verbose_name='Embedding')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.CharField(max_length=6, primary_key=True, serialize=False, unique=True, verbose_name='Person ID')),
                ('crop_ids', models.JSONField(default=list, verbose_name='Crops list')),
            ],
        ),
    ]
