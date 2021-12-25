from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from questions.models import Subject
from .forms import QuizCreationForm


@login_required
@require_http_methods(['GET', 'POST'])
def quizzes(request, subject_id, subject_slug):
    if request.method == 'POST':
        pass
    else:
        subject = get_object_or_404(Subject, id=subject_id)
        quizzes = subject.quizzes.all()
        authorial_quizzes = request.user.quizzes.filter(subject_id=subject_id).all()
        return render(request, 'quiz/quizzes.html', {'quizzes': quizzes,
                                                     'authorial_quizzes': authorial_quizzes,
                                                     'subject': subject})


@login_required
@require_http_methods(['GET', 'POST'])
def create_quiz(request, subject_id, subject_slug):
    if request.method == 'POST':
        quiz_form = QuizCreationForm(data=request.POST)
        if quiz_form.is_valid():
            new_quiz = quiz_form.save(commit=False)
            new_quiz.author = request.user
            new_quiz.subject = get_object_or_404(Subject, id=subject_id)
            new_quiz.save()
            return redirect(reverse('quiz:quizzes', args=[subject_id, subject_slug]))
    else:
        quiz_form = QuizCreationForm()
    return render(request, 'quiz/quiz_create.html', {'quiz_form': quiz_form,
                                                     'subject': get_object_or_404(Subject, id=subject_id)})


@login_required
@require_http_methods(['GET', 'POST'])
def quiz(request, subject_id, subject_slug, quiz_id, quiz_slug):
    pass
