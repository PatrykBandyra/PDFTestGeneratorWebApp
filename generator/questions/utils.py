def is_author_of_subject(user, subject_id):
    """
    Checks if an user is an author of a subject with given id.
    Being an author allows user to change name and description of a subject and delete the subject.
    An author can also manage all questions assigned to a subject.
    """
    return True if subject_id in user.subjects_owned.all().values_list('id', flat=True) else False


def is_owner_of_subject(user, subject_id):
    """
    Checks if an user is an owner of a subject with given id.
    Being an owner allows user to add questions and modify and delete questions added by itself.
    """
    return True if subject_id in user.subjects.all().values_list('id', flat=True) else False
