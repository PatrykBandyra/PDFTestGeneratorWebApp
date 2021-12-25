import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from questions.models import Subject
from .forms import QuizCreationForm
from .utils import is_author_of_quiz
from .models import Quiz
from questions.utils import is_author_of_subject


@login_required
@require_http_methods(['GET', 'POST'])
def quizzes(request, subject_id, subject_slug):
    if request.method == 'POST':

        # Quiz deletion
        quiz_to_delete_id = request.POST.get('delete')
        if quiz_to_delete_id:
            try:
                quiz_to_delete_id = int(quiz_to_delete_id)
                # Check if user is an author of a quiz or an author of a subject - only those can delete a quiz
                if not is_author_of_quiz(request.user, quiz_to_delete_id) and \
                        not is_author_of_subject(request.user, subject_id):
                    raise Exception

                Quiz.objects.get(id=quiz_to_delete_id).delete()

            except Exception:
                return redirect('account:dashboard')

        # Quiz copy
        quiz_to_copy_id = request.POST.get('copy')
        if quiz_to_copy_id:
            try:
                quiz_to_copy_id = int(quiz_to_copy_id)
                # Check if user is an author of a quiz or an author of a subject - only those can delete a quiz
                if not is_author_of_quiz(request.user, quiz_to_copy_id) and \
                        not is_author_of_subject(request.user, subject_id):
                    raise Exception

                quiz = Quiz.objects.get(id=quiz_to_copy_id)
                quiz.id = None
                quiz.save()

            except Exception:
                return redirect('account:dashboard')

    # GET/POST
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = subject.quizzes.all().order_by('-id')

    paginator = Paginator(quizzes, 12)
    page = request.GET.get('page')
    try:
        quizzes_page = paginator.page(page)
    except PageNotAnInteger:
        # If page value is not int - get first page
        quizzes_page = paginator.page(1)
    except EmptyPage:
        # If page value is bigger than the value of last page - get last page
        quizzes_page = paginator.page(paginator.num_pages)

    if is_author_of_subject(request.user, subject.id):
        authorial_quizzes = quizzes
    else:
        authorial_quizzes = request.user.quizzes.filter(subject_id=subject_id).all()
    return render(request, 'quiz/quizzes.html', {'quizzes': quizzes_page,
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
                                                     'subject': get_object_or_404(Subject, id=subject_id),
                                                     'section': 'create_quiz'})


@login_required
@require_http_methods(['GET', 'POST'])
def edit_quiz(request, subject_id, subject_slug, quiz_id, quiz_slug):
    # Check if user is an author of a quiz or an author of a subject
    if not is_author_of_quiz(request.user, quiz_id) and not is_author_of_subject(request.user, subject_id):
        # Just redirect - do not inform about illegal action
        return redirect(reverse('quiz:quizzes', args=[subject_id, subject_slug]))

    if request.method == 'POST':
        quiz_form = QuizCreationForm(data=request.POST)
        if quiz_form.is_valid():
            quiz = get_object_or_404(Quiz, id=quiz_id)
            quiz.name = quiz_form.cleaned_data['name']
            quiz.description = quiz_form.cleaned_data['description']

            # Remove tags
            for tag in quiz.tags.all():
                if tag.name not in re.split(', |,| ', quiz_form.data.get('tags')):
                    quiz.tags.remove(tag)

            # Add tags
            for tag in re.split(', |,| ', quiz_form.data.get('tags')):
                quiz.tags.add(tag.strip())

            quiz.save()
            return redirect(reverse('quiz:quizzes', args=[subject_id, subject_slug]))
    else:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        subject = get_object_or_404(Subject, id=subject_id)
        quiz_form = QuizCreationForm(instance=quiz)
        return render(request, 'quiz/quiz_create.html', {'quiz_form': quiz_form, 'section': 'edit_quiz',
                                                         'quiz': quiz, 'subject': subject})


@login_required
@require_http_methods(['GET', 'POST'])
def quiz(request, subject_id, subject_slug, quiz_id, quiz_slug):
    pass
