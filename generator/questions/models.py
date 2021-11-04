from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Subject(models.Model):
    name = models.CharField(max_length=100)  # Only field required in form
    slug = models.SlugField(blank=True)  # Generated automatically on creation
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects_owned')
    ownership = models.ManyToManyField(User, related_name='subjects')
    description = models.CharField(max_length=250, blank=True)

    __original_name = None

    def __init__(self, *args, **kwargs):
        super(Subject, self).__init__(*args, **kwargs)
        self.__original_name = self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Create slug only when object is being created or name has been updated
        if not self.id or self.name != self.__original_name:
            self.slug = slugify(self.name)
        super(Subject, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('questions:subject', args=[self.id, self.slug])


class Question(models.Model):
    question = models.TextField(max_length=1000)
    # usage
    # tags
    # code_snippet
    # author =


class Answer(models.Model):
    pass
