from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
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

class QuizViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('Name')
        cls.factory = RequestFactory()
        cls.subject = Subject.objects.create(name='Maths', author=cls.user)
        cls.question = Question.objects.create(author=cls.user, subject=cls.subject, question="pancakes?")

    def test_quizzes_get_form(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'query': 'query', 'tag_query': 'blah'})
        request.user = self.user
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_quizzes_get_form_empty_page(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'query': 'query', 'tag_query': 'blah', 'page': 3})
        request.user = self.user
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_quizzes_get_form_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'query': 'query', 'tag_query': 'blah'})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_quizzes_delete_quiz(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'delete': quiz.id})
        request.user = self.user
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.all().first(), None)

    def test_quizzes_delete_quiz_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'delete': quiz.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first(), quiz)

    def test_quizzes_copy_quiz(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'copy': quiz.id})
        request.user = self.user
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.filter(id=quiz.id + 1).get().name, quiz.name)
        
    def test_quizzes_copy_quiz_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug]), data={'copy': quiz.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quizzes(request, self.subject.id, self.subject.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.filter(id=quiz.id+1).first(), None)

    def test_quiz_create_get_form(self):
        request = self.factory.get(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]))
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        self.assertEqual(response.status_code, 200)

    def test_quiz_create_new(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first().name, 'new quiz')
    
    def test_quiz_edit_get_form(self):
        quiz = Quiz.objects.create(name='test quiz', author=self.user, subject=self.subject)
        request = self.factory.get(reverse('quiz:edit-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]))
        request.user = self.user
        response = edit_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug)
        self.assertEqual(response.status_code, 200)

    def test_quiz_edit_not_author(self):
        user2 = User.objects.create_user("Name2")
        quiz = Quiz.objects.create(name='test quiz', author=self.user, subject=self.subject)
        request = self.factory.get(reverse('quiz:edit-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]))
        request.user = user2
        response = edit_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug)
        self.assertEqual(response.status_code, 302)

    def test_quiz_edit_with_ret(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:edit-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'name': 'new quiz2', 'description': 'quizzz', 'tags': 'blah2', 'ret': reverse('quiz:quizzes', args=[self.subject.id, self.subject.slug])})
        request.user = self.user
        response = edit_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first().description, 'quizzz')

    def test_quiz_edit_without_ret(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:edit-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'name': 'new quiz2', 'description': 'quizzz', 'tags': 'blah2'})
        request.user = self.user
        response = edit_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first().description, 'quizzz')

    def test_quiz_get_form(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'query': 'query', 'tag_query': 'blah'})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_quiz_get_form_empty_page(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'query': 'query', 'tag_query': 'blah', 'page': 3})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_quiz_delete(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'delete_quiz': quizz.id})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first(), None)

    def test_quiz_delete_bad_id(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'delete_quiz': "not a number"})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first(), quizz)

    def test_quiz_delete_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'delete_quiz': quizz.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.all().first(), quizz)

    def test_quiz_delete_question(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)

        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'delete': self.question.id})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(QuizQuestion.objects.all().first(), None)

    def test_quiz_delete_question_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)

        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'delete': self.question.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(QuizQuestion.objects.all().first(), quizquestion)

    def test_quiz_question_move_up(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')
        quizquestion2 = QuizQuestion.objects.create(quiz=quizz, question=question2, order=2)


        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'up': question2.id})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(QuizQuestion.objects.filter(order=1).get().question, question2)

    def test_quiz_question_move_up_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')
        quizquestion2 = QuizQuestion.objects.create(quiz=quizz, question=question2, order=2)


        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'up': question2.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(QuizQuestion.objects.filter(order=2).get().question, question2)

    def test_quiz_question_move_down(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')
        quizquestion2 = QuizQuestion.objects.create(quiz=quizz, question=question2, order=2)


        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'down': self.question.id})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(QuizQuestion.objects.filter(order=2).get().question, self.question)

    def test_quiz_question_move_down_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')
        quizquestion2 = QuizQuestion.objects.create(quiz=quizz, question=question2, order=2)


        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'down': self.question.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(QuizQuestion.objects.filter(order=1).get().question, self.question)

    def test_quiz_question_randomize(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quizz = Quiz.objects.all().first()
        quizquestion = QuizQuestion.objects.create(quiz=quizz, question=self.question, order=1)
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')
        quizquestion2 = QuizQuestion.objects.create(quiz=quizz, question=question2, order=2)


        request = self.factory.post(reverse('quiz:quiz', args=[self.subject.id, self.subject.slug, quizz.id, quizz.slug]), data={'randomize': 'yes'})
        request.user = self.user
        response = quiz(request, self.subject.id, self.subject.slug, quizz.id, quizz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_add_quiz_get_form(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'query': 'query', 'tag_query': 'blah'})
        request.user = self.user
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_add_quiz_get_form_empty_page(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'query': 'query', 'tag_query': 'blah', 'page': 3})
        request.user = self.user
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)

    def test_add_quiz_question(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'add': self.question.id})
        request.user = self.user
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuizQuestion.objects.all().first().question, self.question)

    def test_add_quiz_question_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.post(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'add': self.question.id})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuizQuestion.objects.all().first(), None)

    def test_add_quiz_question_next_order(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')
        quizquestion2 = QuizQuestion.objects.create(quiz=quiz, question=question2, order=1)

        request = self.factory.post(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'add': self.question.id})
        request.user = self.user
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuizQuestion.objects.filter(order=2).get().question, self.question)

    def test_add_quiz_questions(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')

        request = self.factory.post(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'add_all': f'{self.question.id},{question2.id}'})
        request.user = self.user
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuizQuestion.objects.filter(order=1).get().question, self.question)

    def test_add_quiz_questions_not_author(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()
        question2 = Question.objects.create(author=self.user, subject=self.subject, question='do you like pancakes?')

        request = self.factory.post(reverse('quiz:add-question-to-quiz', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]), data={'add_all': f'{self.question.id},{question2.id}'})
        user2 = User.objects.create_user("Name2")
        request.user = user2
        response = add_question_to_quiz(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug, tag_slug=slugify('blah'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuizQuestion.objects.all().first(), None)

        

    def test_quiz_get_pdf(self):
        request = self.factory.post(reverse('quiz:create-quiz', args=[self.subject.id, self.subject.slug]), data={'name': 'new quiz', 'author': self.user, 'subject': self.subject, 'tags': 'blah'})
        request.user = self.user
        response = create_quiz(request, self.subject.id, self.subject.slug)
        quiz = Quiz.objects.all().first()

        request = self.factory.get(reverse('quiz:quiz-pdf', args=[self.subject.id, self.subject.slug, quiz.id, quiz.slug]))
        request.user = self.user
        response = quiz_pdf(request, self.subject.id, self.subject.slug, quiz.id, quiz.slug)
        self.assertEqual(response.status_code, 200)