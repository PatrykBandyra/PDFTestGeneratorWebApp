from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from questions.models import Question, Subject


class Quiz(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)  # Generated automatically on creation
    description = models.CharField(max_length=250, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    tags = TaggableManager(blank=True)

    __original_name = None

    def __init__(self, *args, **kwargs):
        super(Quiz, self).__init__(*args, **kwargs)
        self.__original_name = self.name

    def __str__(self):
        return f'ID: {self.id}, NAME: {self.name}'

    def save(self, *args, **kwargs):
        # Create slug only when object is being created or name has been updated
        if not self.id or self.name != self.__original_name:
            self.slug = slugify(self.name)
        super(Quiz, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, self.id, self.slug])


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_quizzes')
    order = models.IntegerField()

    class Meta:
        # unique_together = ('quiz', 'order')
        required_db_features = {
            'supports_deferrable_unique_constraints'
        }
        constraints = [
            models.UniqueConstraint(
                fields=['quiz', 'order'],
                name='quiz_questions_order_unique',
                deferrable=models.Deferrable.DEFERRED,
            )
        ]


