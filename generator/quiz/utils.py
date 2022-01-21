def is_author_of_quiz(user, quiz_id):
    """
    Checks of a user is an author of a quiz with given id. Only author of a quiz and author of a subject can delete
    specified quiz.
    """
    return True if quiz_id in user.quizzes.all().values_list('id', flat=True) else False
