from django.db import models
from pgvector.django import VectorField


class Person(models.Model):
    id = models.CharField(
        max_length=6, primary_key=True, unique=True, verbose_name="Person ID"
    )
    crop_ids = models.JSONField(default=list, verbose_name="Crops list")

    def __str__(self):
        return self.id


class Crop(models.Model):
    id = models.CharField(
        max_length=255, primary_key=True, unique=True, verbose_name="Crop ID"
    )
    embedding = VectorField(dimensions=1024, verbose_name="Embedding")

    def __str__(self):
        return self.id
