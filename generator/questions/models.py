from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    ownership = models.ManyToManyField(User, )
