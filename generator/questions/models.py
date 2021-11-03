from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Subject(models.Model):
    name = models.CharField(max_length=100)  # Only name required in a form
    slug = models.SlugField(blank=True, null=False)
    ownership = models.ManyToManyField(User, related_name='subjects_owned', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects_created')
    description = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:  # Create slug only when object is being created
            self.slug = slugify(self.name)
        super(Subject, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('questions:subject', args=[self.author.id, self.slug])


class Question(models.Model):
    question = models.TextField(max_length=1000)
    # usage
    # tags
    # code_snippet
    # author =


class Answer(models.Model):
    pass
