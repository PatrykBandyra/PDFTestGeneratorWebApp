from .models import Question, Answer


def is_author_of_subject(user, subject_id):
    """
    Checks if a user is an author of a subject with given id.
    Being an author allows user to change name and description of a subject and delete the subject.
    An author can also manage all questions assigned to a subject.
    """
    return True if subject_id in user.subjects_owned.all().values_list('id', flat=True) else False


def is_owner_of_subject(user, subject_id):
    """
    Checks if a user is an owner of a subject with given id.
    Being an owner allows user to add questions and modify and delete questions added by itself.
    """
    return True if subject_id in user.subjects.all().values_list('id', flat=True) else False


def is_author_of_question(user, question_id):
    """
    Checks if a user is an author of a question with given id.
    Being an author of a question allows user to delete and modify it.
    """
    return True if question_id in user.questions.all().values_list('id', flat=True) else False


def is_answer_unique_constraint_fulfilled(question_id, order):
    """
    Checks if an answer does not validate a unique constraint (Question, order).
    For usage in views to validate user input.
    """
    return True if not Answer.objects.filter(question=question_id, order=int(order)) else False
