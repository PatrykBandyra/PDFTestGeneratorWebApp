from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

from .models import Quiz, QuizQuestion
from .utils import *
from .views import *

class QuizModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name')
        cls.factory = RequestFactory()

    def test_str(self):
        subject = Subject.objects.create(name="Maths", author=self.user)
        quiz = Quiz(name="quiz", author=self.user, subject=subject)
        self.assertEqual(quiz.__str__(), f'ID: {quiz.id}, NAME: quiz')

    def test_save(self):
        subject = Subject.objects.create(name="Maths", author=self.user)
        quiz = Quiz(name="quiz", author=self.user, subject=subject)
        quiz.save()
        self.assertEqual(quiz.slug, 'quiz')
        quiz.name = "changedquiz"
        quiz.save()
        self.assertEqual(quiz.slug, slugify("changedquiz"))

    def test_url(self):
        subject = Subject.objects.create(name="Maths", author=self.user)
        quiz = Quiz(name="quiz", author=self.user, subject=subject)
        quiz.save()
        expected_url = reverse('quiz:quiz', args=[subject.id, subject.slug, quiz.id, quiz.slug])
        self.assertEqual(expected_url, quiz.get_absolute_url())

class UtilsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name')
        cls.factory = RequestFactory()
    
    def test_check_author(self):
        subject = Subject.objects.create(name="Maths", author=self.user)
        quiz = Quiz(name="quiz", author=self.user, subject=subject)
        quiz.save()
        self.assertTrue(is_author_of_quiz(self.user, quiz.id))
