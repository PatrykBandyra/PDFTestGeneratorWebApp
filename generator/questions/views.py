from django.shortcuts import render


def subject(request, user_id, subject_name):
    return render(request, 'questions/subject.html', {})
