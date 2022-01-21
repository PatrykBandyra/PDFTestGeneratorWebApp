from django.db.utils import IntegrityError
from django.test import TestCase, RequestFactory
from django.utils.text import slugify

from .views import *


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

class UtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.subject = Subject.objects.create(name='PPP', author=cls.user)
        cls.question = Question.objects.create(question='PPP', subject=cls.subject, author=cls.user)
        cls.answer = Answer.objects.create(answer='PPP', question=cls.question, order=1)

    def test_author_of_subject(self):
        user2 = User.objects.create_user('Name2')
        self.subject.ownership.add(self.user, user2)
        self.assertTrue(is_author_of_subject(self.user, self.subject.id))
        self.assertFalse(is_author_of_subject(user2, self.subject.id))

    def test_owner_of_subject(self):
        user2 = User.objects.create_user('Name2')
        self.subject.ownership.add(self.user, user2)
        self.assertTrue(is_owner_of_subject(self.user, self.subject.id))
        self.assertTrue(is_owner_of_subject(user2, self.subject.id))

    def test_author_of_question(self):
        self.assertTrue(is_author_of_question(self.user, self.question.id))

    def test_answer_unique_constraint_fulfilled(self):
        self.assertFalse(is_answer_unique_constraint_fulfilled(self.question.id, 1))


class SubjectViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.user2 = User.objects.create_user('Name2')
        cls.factory = RequestFactory()

    def test_create_subject_get_form(self):
        request = self.factory.get(reverse("questions:subject-create"))
        request.user = self.user
        response = create_subject(request)
        self.assertEqual(response.status_code, 200)
        

    def test_create_subject_add_subject(self):
        request = self.factory.post(reverse("questions:subject-create"), data={"name": "PPP", "description": "BBB"})
        request.user = self.user
        response = create_subject(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subject.objects.all().first().author, self.user)

    def test_edit_subject_not_author(self):
        subject = Subject.objects.create(name='PPP', author=self.user)
        request = self.factory.post(reverse("questions:subject-edit", args=[subject.id, slugify(subject.name)]), data={"name": "RRR", "description": "CCC"})
        request.user = self.user2
        response = edit_subject(request, subject.id, slugify(subject.name))
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(Subject.objects.all().first().name, 'RRR')

    def test_edit_subject_author_edit(self):
        subject = Subject.objects.create(name='PPP', author=self.user)
        request = self.factory.post(reverse("questions:subject-edit", args=[subject.id, slugify(subject.name)]), data={"name": "RRR", "description": "CCC"})
        request.user = self.user
        response = edit_subject(request, subject.id, slugify(subject.name))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subject.objects.all().first().name, 'RRR')

    def test_edit_subject_author_get_form(self):
        subject = Subject.objects.create(name='PPP', author=self.user)
        request = self.factory.get(reverse("questions:subject-edit", args=[subject.id, slugify(subject.name)]))
        request.user = self.user
        response = edit_subject(request, subject.id, slugify(subject.name))
        self.assertEqual(response.status_code, 200)

    def test_subject_delete_questions(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.post(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={"delete": question.id})
        request.user = self.user
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.all().first(), None)

    def test_subject_delete_questions_exception(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.post(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={"delete": "not a number"})
        request.user = self.user
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(Question.objects.all().first(), None)

    def test_subject_delete_questions_exception_bad_user(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.post(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={"delete": question.id})
        request.user = self.user2
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(Question.objects.all().first(), None)

    def test_subject_search_query(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        subjects.ownership.add(self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.get(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={'query': 'query'})
        request.user = self.user
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 200)

    def test_subject_search_query_ajax(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        subjects.ownership.add(self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.get(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), HTTP_X_REQUESTED_WITH='XMLHttpRequest', data={'query': 'query'})
        request.user = self.user
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 200)

    def test_subject_search_tag(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        subjects.ownership.add(self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.get(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={'tag_query': 'tag'})
        request.user = self.user
        
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 200)

    def test_subject_search_query_empty_page(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        subjects.ownership.add(self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.get(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={'query': 'query', 'page': 3})
        request.user = self.user
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 200)

    def test_subject_search_query_empty_page_ajax(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        subjects.ownership.add(self.user)
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.get(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), HTTP_X_REQUESTED_WITH='XMLHttpRequest', data={'query': 'query', 'page': 3})
        request.user = self.user
        response = subject(request, subjects.id, slugify(subjects.name))
        self.assertEqual(response.status_code, 200)

    def test_subject_search_query_tag(self):
        subjects = Subject.objects.create(name='PPP', author=self.user)
        subjects.ownership.add(self.user)

        request = self.factory.post(reverse("questions:question-create", args=[subjects.id, slugify(subjects.name)]), data={"question": "PPP", 'tags': 'blah'})
        request.user = self.user
        response = create_question(request, subjects.id, slugify(subjects.name))
        question = Question.objects.all().first()
        
        
        question = Question.objects.create(question='PPP', subject=subjects, author=self.user)
        request = self.factory.get(reverse("questions:subject", args=[subjects.id, slugify(subjects.name)]), data={'query': 'query'})
        request.user = self.user
        response = subject(request, subjects.id, slugify(question.tags), slugify('blah'))
        self.assertEqual(response.status_code, 200)

        

class QuestionViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.user2 = User.objects.create_user('Name2')
        cls.subject = Subject.objects.create(name='PPP', author=cls.user)
        cls.question = Question.objects.create(question='QQQ', author=cls.user, subject=cls.subject)
        cls.answer = Answer.objects.create(question=cls.question, order=1)
        cls.answer2 = Answer.objects.create(question=cls.question, order=2)
        cls.factory = RequestFactory()

    def test_create_question_get_form(self):
        request = self.factory.get(reverse("questions:question-create", args=[self.subject.id, slugify(self.subject.name)]))
        request.user = self.user
        response = create_question(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)

    def test_create_question_add_question(self):
        request = self.factory.post(reverse("questions:question-create", args=[self.subject.id, slugify(self.subject.name)]), data={"question": "PPP"})
        request.user = self.user
        response = create_question(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.all().first().author, self.user)

    def test_edit_question_get_form(self):
        request = self.factory.get(reverse("questions:question-edit", args=[self.subject.id, slugify(self.subject.name), self.question.id]))
        request.user = self.user
        response = edit_question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 200)

    def test_edit_question_get_not_author(self):
        request = self.factory.get(reverse("questions:question-edit", args=[self.subject.id, slugify(self.subject.name), self.question.id]))
        request.user = self.user2
        response = edit_question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)

    def test_edit_question(self):
        request = self.factory.post(reverse("questions:question-create", args=[self.subject.id, slugify(self.subject.name)]), data={"question": "PPP", 'tags': 'blah'})
        request.user = self.user
        response = create_question(request, self.subject.id, slugify(self.subject.name))
        question2 = Question.objects.all().first()

        new_question = 'QQQQ'
        request = self.factory.post(reverse("questions:question-edit", args=[self.subject.id, slugify(self.subject.name), question2.id]), data={'question': new_question, 'tags': 'blah2'})
        request.user = self.user
        response = edit_question(request, self.subject.id, slugify(self.subject.name), question2.id)
        self.assertEqual(Question.objects.all().first().question, new_question)

    def test_question_not_author(self):
        request = self.factory.get(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]))
        request.user = self.user2
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)

    def test_question_get_form(self):
        request = self.factory.get(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]))
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 200)

    def test_question_delete_question(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'delete-question': self.question.id})
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.all().first(), None)

    def test_question_delete_question_bad_id(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'delete-question': "not a number"})
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.all().first(), self.question)

    def test_question_delete_question_answers(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'delete-answer': self.answer.id})
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.all().first(), self.answer2)

    def test_question_delete_question_answers_bad_id(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'delete-answer': "not a number"})
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.all().first(), self.answer)

    def test_question_move_answer_up(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'up': self.answer2.id})
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.filter(id=self.answer2.id).get().order, 1)
        self.assertEqual(Answer.objects.filter(id=self.answer.id).get().order, 2)

    def test_question_move_answer_up_highest(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'up': self.answer.id})
        request.user = self.user
        exception = False
        try:
            response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        except:
            exception = True
        self.assertTrue(exception)

    def test_question_move_answer_down(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'down': self.answer.id})
        request.user = self.user
        response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.filter(id=self.answer2.id).get().order, 1)
        self.assertEqual(Answer.objects.filter(id=self.answer.id).get().order, 2)

    def test_question_move_answer_down_lowest(self):
        request = self.factory.post(reverse("questions:question", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'down': self.answer2.id})
        request.user = self.user
        exception = False
        try:
            response = question(request, self.subject.id, slugify(self.subject.name), self.question.id)
        except:
            exception = True
        self.assertTrue(exception)

    
class AnswerViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.user2 = User.objects.create_user('Name2')
        cls.subject = Subject.objects.create(name='PPP', author=cls.user)
        cls.question = Question.objects.create(question='QQQ', author=cls.user, subject=cls.subject)
        cls.answer = Answer.objects.create(question=cls.question, order=1)
        cls.answer2 = Answer.objects.create(question=cls.question, order=2)
        cls.factory = RequestFactory()

    def test_answer_add_not_author(self):
        request = self.factory.get(reverse("questions:question-add-answer", args=[self.subject.id, slugify(self.subject.name), self.question.id]))
        request.user = self.user2
        response = add_answer(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
    
    def test_answer_add_get_form(self):
        request = self.factory.get(reverse("questions:question-add-answer", args=[self.subject.id, slugify(self.subject.name), self.question.id]))
        request.user = self.user
        response = add_answer(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 200)

    def test_answer_add_get_form_no_answers_yet(self):
        question2 = Question.objects.create(question='QQQ', author=self.user, subject=self.subject)
        request = self.factory.get(reverse("questions:question-add-answer", args=[self.subject.id, slugify(self.subject.name), question2.id]))
        request.user = self.user
        response = add_answer(request, self.subject.id, slugify(self.subject.name), question2.id)
        self.assertEqual(response.status_code, 200)

    def test_answer_add_new(self):
        request = self.factory.post(reverse("questions:question-add-answer", args=[self.subject.id, slugify(self.subject.name), self.question.id]), data={'answer': 'a', 'question': self.question, 'order': 3})
        request.user = self.user
        response = add_answer(request, self.subject.id, slugify(self.subject.name), self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.filter(order=3).get().question, self.question)

    def test_answer_edit_not_author(self):
        request = self.factory.get(reverse("questions:question-edit-answer", args=[self.subject.id, slugify(self.subject.name), self.question.id, self.answer.id]))
        request.user = self.user2
        response = edit_answer(request, self.subject.id, slugify(self.subject.name), self.question.id, self.answer.id)
        self.assertEqual(response.status_code, 302)

    def test_answer_edit_get_form(self):
        request = self.factory.get(reverse("questions:question-edit-answer", args=[self.subject.id, slugify(self.subject.name), self.question.id, self.answer.id]))
        request.user = self.user
        response = edit_answer(request, self.subject.id, slugify(self.subject.name), self.question.id, self.answer.id)
        self.assertEqual(response.status_code, 200)

    def test_answer_edit_answer(self):
        request = self.factory.post(reverse("questions:question-edit-answer", args=[self.subject.id, slugify(self.subject.name), self.question.id, self.answer.id]), data={'answer': 'nowy tekst', 'question': self.question, 'order': 3})
        request.user = self.user
        response = edit_answer(request, self.subject.id, slugify(self.subject.name), self.question.id, self.answer.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.filter(order=3).get().answer, 'nowy tekst')


class AdditionalViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up data for the whole TestCase
        """
        cls.user = User.objects.create_user('Name')
        cls.user2 = User.objects.create_user('Name2')
        cls.subject = Subject.objects.create(name='PPP', author=cls.user)
        cls.subject.ownership.add(cls.user)
        cls.question = Question.objects.create(question='QQQ', author=cls.user, subject=cls.subject)
        cls.answer = Answer.objects.create(question=cls.question, order=1)
        cls.answer2 = Answer.objects.create(question=cls.question, order=2)
        cls.factory = RequestFactory()

    def test_people_remove_ownership(self):
        request = self.factory.post(reverse("questions:subject-people", args=[self.subject.id, slugify(self.subject.name)]), data={'delete': self.user.id})
        request.user = self.user
        response = people(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(is_owner_of_subject(self.user, self.subject.id))

    def test_people_not_author(self):
        request = self.factory.post(reverse("questions:subject-people", args=[self.subject.id, slugify(self.subject.name)]), data={'delete': self.user.id})
        request.user = self.user2
        response = people(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 302)

    def test_people_remove_ownership_bad_id(self):
        request = self.factory.post(reverse("questions:subject-people", args=[self.subject.id, slugify(self.subject.name)]), data={'delete': "not a number"})
        request.user = self.user
        response = people(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_owner_of_subject(self.user, self.subject.id))

    def test_people_add_ownership(self):
        request = self.factory.post(reverse("questions:subject-add-owner", args=[self.subject.id, slugify(self.subject.name)]), data={'user_id': self.user.id})
        request.user = self.user
        response = add_owner(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_owner_of_subject(self.user, self.subject.id))

    def test_people_add_ownership_not_author(self):
        request = self.factory.post(reverse("questions:subject-add-owner", args=[self.subject.id, slugify(self.subject.name)]), data={'user_id': self.user.id})
        request.user = self.user2
        response = add_owner(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 302)

    def test_people_add_ownership_bad_id(self):
        request = self.factory.post(reverse("questions:subject-add-owner", args=[self.subject.id, slugify(self.subject.name)]), data={'user_id': "not a number"})
        request.user = self.user
        response = add_owner(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)

    def test_people_add_ownership_with_query(self):
        request = self.factory.get(reverse("questions:subject-add-owner", args=[self.subject.id, slugify(self.subject.name)]), data={'query': 'query'})
        request.user = self.user
        response = add_owner(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)

    def test_people_add_ownership_with_query_empty_page(self):
        request = self.factory.get(reverse("questions:subject-add-owner", args=[self.subject.id, slugify(self.subject.name)]), data={'query': 'query', 'page': 3})
        request.user = self.user
        response = add_owner(request, self.subject.id, slugify(self.subject.name))
        self.assertEqual(response.status_code, 200)