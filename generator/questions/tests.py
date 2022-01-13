from django.db.utils import IntegrityError

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

from .models import Subject, Question, Answer
from .utils import *


class SubjectModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.user2 = User.objects.create_user('Name2')

    def test_name_field(self):
        """
        Tests if subject.name can be changed as expected.
        Success if name is changed successfully.
        """
        id = Subject.objects.create(name='Polish', author=self.user).id
        subject = Subject.objects.filter(id=id).first()
        subject.name = 'German'
        subject.save()
        subject = Subject.objects.filter(id=id).first()
        self.assertEqual('German', subject.name)

    def test_description_field(self):
        """
        Tests if subject.description can be changed as expected.
        Success if description is changed successfully.
        """
        description = 'I like bananas'
        id = Subject.objects.create(name='ZZZ', author=self.user, description=description).id
        subject = Subject.objects.filter(id=id).first()
        updated_description = 'Cool subject'
        subject.description = updated_description
        subject.save()
        subject = Subject.objects.filter(id=id).first()
        self.assertEqual(updated_description, subject.description)

    def test_slug_auto_creation(self):
        """
        Tests creation of subject.slug field that is supposed to be generated on creation.
        Success if slug is created.
        """
        name = 'Math and Physics'
        subject = Subject.objects.create(name=name, author=self.user)
        self.assertEqual(slugify(name), subject.slug)

    def test_slug_is_updated_after_name_change(self):
        """
        Tests if slug is updated after subject.name change.
        Success if slug updated.
        """
        subject = Subject.objects.create(name='Chemistry', author=self.user)
        updated_name = 'Philosophy'
        subject.name = updated_name
        subject.save()
        subject = Subject.objects.filter(id=subject.id).first()
        self.assertEqual(slugify(updated_name), subject.slug)

    def test_unique_together_name_and_author(self):
        """
        Tests UNIQUE constraint on (subject.name & subject.author) couple.
        Success if Integrity error caught.
        """
        exception_raised = False
        Subject.objects.create(name='Math', author=self.user)
        try:
            Subject.objects.create(name='Math', author=self.user)
        except IntegrityError:
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_multiple_ownership_of_subject(self):
        """
        Tests if 2 users (author and other) can own subject and access it.
        Success if they can.
        """
        subject = Subject(name='XYZ', author=self.user)
        subject.save()
        subject.ownership.add(self.user, self.user2)
        s1 = self.user.subjects.filter(id=subject.id).first()
        s2 = self.user2.subjects.filter(id=subject.id).first()
        self.assertEqual(s1, s2)

    def test_if_changes_made_by_one_owner_will_be_visible_to_the_other(self):
        """
        Tests if changes made to a subject by one owner will be visible to others.
        Success if changes visible.
        """
        subject = Subject(name='ABCDEF', author=self.user)
        subject.save()
        subject.ownership.add(self.user, self.user2)
        s1 = self.user.subjects.filter(id=subject.id).first()
        updated_name = 'Alohomora'
        s1.name = updated_name
        s1.save()
        s2 = self.user2.subjects.filter(id=subject.id).first()
        self.assertEqual(updated_name, s2.name)

    def test_get_absolute_url(self):
        subject = Subject.objects.create(name='PPP', author=self.user)
        expected_url = reverse('questions:subject', args=[subject.id, slugify(subject.name)])
        self.assertEqual(expected_url, subject.get_absolute_url())

    def test_get_str(self):
        subject_name = 'PPP'
        subject = Subject.objects.create(name=subject_name, author=self.user)
        self.assertEqual(subject.__str__(), subject_name)


class QuestionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.subject = Subject.objects.create(name='PPP', author=cls.user)

    def test_get_str(self):
        question = Question.objects.create(question='PPP', subject=self.subject, author=self.user)
        self.assertEqual(question.__str__(), f'ID: {question.id}, AUTHOR: {self.user.username}')

    def test_get_absolute_url(self):
        question = Question.objects.create(question='PPP', subject=self.subject, author=self.user)
        expected_url = reverse('questions:question', args=[self.subject.id, slugify(question.question), question.id])
        self.assertEqual(expected_url, question.get_absolute_url())

class AnswerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.subject = Subject.objects.create(name='PPP', author=cls.user)
        cls.question = Question.objects.create(question='PPP', subject=cls.subject, author=cls.user)

    def test_get_str(self):
        answer = Answer.objects.create(answer='PPP', question=self.question, order=1)
        self.assertEqual(answer.__str__(), f'ID: {answer.id}, QUESTION ID: {self.question.id}')
