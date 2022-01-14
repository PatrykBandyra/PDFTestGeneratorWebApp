from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.utils.text import slugify
from django.urls import reverse

from .views.views_logged import *
from .views.views_logging import *
from .forms import *
from .authentication import *

class ViewsLoggedTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name')
        cls.factory = RequestFactory()
    
    def test_dashboard_get(self):
        request = self.factory.get(reverse("account:dashboard"))
        request.user = self.user
        response = dashboard(request)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_delete_subject(self):
        subject = Subject.objects.create(name="Physics", author=self.user)
        request = self.factory.post(reverse("account:dashboard"), data={'delete': subject.id})
        request.user = self.user
        response = dashboard(request)
        self.assertEqual(Subject.objects.all().first(), None)

    def test_dashboard_delete_subject_not_author(self):
        subject = Subject.objects.create(name="Physics", author=self.user)
        user2 = User.objects.create_user('Name2')
        request = self.factory.post(reverse("account:dashboard"), data={'delete': subject.id})
        request.user = user2
        response = dashboard(request)
        self.assertEqual(Subject.objects.all().first(), subject)

class ViewsLoggingTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name')
        cls.factory = RequestFactory()

    def test_main_authenticated(self):
        request = self.factory.get(reverse("account:main"))
        request.user = self.user
        response = main(request)
        self.assertEqual(response.status_code, 302)

    def test_main_anonymous(self):
        request = self.factory.get(reverse("account:main"))
        request.user = AnonymousUser()
        response = main(request)
        self.assertEqual(response.status_code, 200)

    def test_register_get_form(self):
        request = self.factory.get(reverse("account:register"))
        request.user = self.user
        response = register(request)
        self.assertEqual(response.status_code, 200)

    def test_register_new(self):
        request = self.factory.post(reverse("account:register"), data={'username': 'username', 'first_name': 'first_name', 'last_name': 'last_name', 'email': 'username@email.com', 'password1': 'password12341234', 'password2': 'password12341234'})
        request.user = self.user
        response = register(request)
        self.assertEqual(response.status_code, 200)

class FormsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name')
        cls.factory = RequestFactory()

    def test_forms_creation(self):
        form_reset_password = CustomResetPasswordForm(self.user)
        form_reset_password_confirm = CustomResetPasswordConfirmForm(self.user)
        form_change_password = CustomChangePasswordForm(self.user)
        form_login = CustomLoginForm(self.user)

class AuthenticationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name', 'name@email.com', 'namepass1234')
        cls.factory = RequestFactory()
        cls.auth = EmailAuthBackend()

    def test_user_get_correct(self):
        user = self.auth.get_user(self.user.id)
        self.assertEqual(user, self.user)

    def test_user_get_incorrect(self):
        user = self.auth.get_user(1234)
        self.assertEqual(user, None)

    def test_user_authenticate_accept(self):
        user = self.auth.authenticate(None, username='name@email.com', password='namepass1234')
        self.assertEqual(self.user, user)

    def test_user_authenticate_bad_username(self):
        user = self.auth.authenticate(None, username='username', password='password')
        self.assertEqual(user, None)

    def test_user_authenticate_bad_password(self):
        user = self.auth.authenticate(None, username='name@email.com', password='password')
        self.assertEqual(user, None)
