from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET, require_http_methods
from .forms import SubjectCreationForm, QuestionCreationForm
from .models import Subject, Question, Answer
from .utils import is_author_of_subject, is_owner_of_subject, is_author_of_question


@login_required
@require_http_methods(['GET', 'POST'])
def create_subject(request):
    if request.method == 'POST':
        subject_form = SubjectCreationForm(data=request.POST)
        if subject_form.is_valid():
            new_subject = subject_form.save(commit=False)
            new_subject.author = request.user
            new_subject.save()  # First subject needs to get the id before ownership can be added
            new_subject.ownership.add(request.user)
            new_subject.save()
            return redirect('account:dashboard')
    else:
        subject_form = SubjectCreationForm()
    return render(request, 'questions/subject_form.html', {'subject_form': subject_form, 'section': 'create_subject'})


@login_required
@require_http_methods(['GET', 'POST'])
def edit_subject(request, subject_id, subject_slug):
    # Check if user is an author of a subject - only author can edit a subject (name, description)
    if not is_author_of_subject(request.user, subject_id):
        return redirect('account:dashboard')  # Just redirect - do not inform about illegal action

    if request.method == 'POST':
        subject_form = SubjectCreationForm(data=request.POST)
        if subject_form.is_valid():
            subject = get_object_or_404(Subject, id=subject_id)
            subject.name = subject_form.cleaned_data['name']
            subject.description = subject_form.cleaned_data['description']
            subject.save()
            return redirect('account:dashboard')
    else:
        subject = get_object_or_404(Subject, id=subject_id)
        subject_form = SubjectCreationForm(instance=subject)
    return render(request, 'questions/subject_form.html', {'subject_form': subject_form, 'section': 'edit_subject'})


@login_required
@require_http_methods(['GET', 'POST'])
def subject(request, subject_id, subject_slug):
    # Question deletion
    if request.method == 'POST':
        try:
            # Check if user is an author of a subject or an author of a question
            question_id = int(request.POST.get('delete'))
            if not is_author_of_question(request.user, question_id) and \
                    not is_owner_of_subject(request.user, subject_id):
                raise Exception

            Question.objects.filter(id=question_id).delete()
        except Exception:
            pass

    # GET (and POST)
    # Check if user is an owner of a subject - only owners can access the subject's questions
    if not is_owner_of_subject(request.user, subject_id):
        return redirect('account:dashboard')

    subject = get_object_or_404(Subject, id=subject_id)
    questions = subject.questions.all()

    return render(request, 'questions/subject_questions.html', {'subject': subject, 'questions': questions})


@login_required
@require_http_methods(['GET', 'POST'])
def create_question(request, subject_id, subject_slug):
    if request.method == 'POST':
        question_form = QuestionCreationForm(data=request.POST)
        if question_form.is_valid():
            new_question = question_form.save(commit=False)
            subject = get_object_or_404(Subject, id=subject_id)
            new_question.subject = subject
            new_question.author = request.user
            new_question.save()
            return redirect(new_question.get_absolute_url())
    else:
        question_form = QuestionCreationForm()
    return render(request, 'questions/question_create.html', {'question_form': question_form})


@login_required
@require_http_methods(['GET', 'POST'])
def question(request, subject_id, subject_slug, question_id):
    # Question deletion
    if request.method == 'POST':
        try:
            # Check if user is an author of a subject or an author of a question
            question_id = int(request.POST.get('delete'))
            if not is_author_of_question(request.user, question_id) and \
                    not is_owner_of_subject(request.user, subject_id):
                raise Exception

            Question.objects.filter(id=question_id).delete()
        except Exception:
            pass
        return redirect(Subject.objects.get(id=subject_id).get_absolute_url())

    else:  # GET
        question = get_object_or_404(Question, id=question_id)
        return render(request, 'questions/question.html', {'question': question, 'answers': question.answers.all()})
