import re

from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.decorators.http import require_http_methods
from taggit.models import Tag
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from .forms import SubjectCreationForm, QuestionCreationForm, AnswerCreationForm, SearchForm, SearchTagForm
from .models import Subject, Question, Answer
from .utils import (is_author_of_subject, is_owner_of_subject, is_author_of_question,
                    is_answer_unique_constraint_fulfilled)


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
        return render(request, 'questions/subject_form.html', {'subject_form': subject_form, 'section': 'edit_subject',
                                                               'subject': subject})


@login_required
@require_http_methods(['GET', 'POST'])
def subject(request, subject_id, subject_slug, tag_slug=None):
    # Question deletion
    if request.method == 'POST':
        try:
            # Check if user is an author of a subject or an author of a question
            question_id = int(request.POST.get('delete'))
            if not is_author_of_question(request.user, question_id) and \
                    not is_author_of_subject(request.user, subject_id):
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

    # Query search - questions and answers
    search_form = SearchForm()
    q = None
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            q = search_form.cleaned_data['query']

            # Rank search
            vector = SearchVector('question', 'answers__answer')
            query = SearchQuery(q)
            questions = questions.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') \
                .distinct()

    # Query search - tags
    tag_search_form = SearchTagForm()
    tag_query = None
    if 'tag_query' in request.GET:
        tag_search_form = SearchTagForm(request.GET)
        if tag_search_form.is_valid():
            tag_query = tag_search_form.cleaned_data['tag_query']
            # Trigram search
            questions = questions.annotate(
                similarity=TrigramSimilarity('tags__name', tag_query)
            ).filter(similarity__gt=0.1).order_by('id', '-similarity').distinct('id')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        questions = questions.filter(tags__in=[tag])

    paginator = Paginator(questions, 10)
    page = request.GET.get('page')
    try:
        questions_page = paginator.page(page)
    except PageNotAnInteger:
        # If page value is not int - get first page
        questions_page = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        # If page value is bigger than the value of last page - get last page
        questions_page = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'questions/subject_questions_ajax.html', {'subject': subject,
                                                                         'questions': questions_page,
                                                                         'tag': tag, 'query': q,
                                                                         'search_form': search_form,
                                                                         'tag_query': tag_query,
                                                                         'tag_search_form': tag_search_form})

    return render(request, 'questions/subject_questions.html', {'subject': subject, 'questions': questions_page,
                                                                'tag': tag, 'query': q,
                                                                'search_form': search_form,
                                                                'tag_query': tag_query,
                                                                'tag_search_form': tag_search_form})


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
            question_form.save_m2m()
            return redirect(new_question.get_absolute_url())
    else:
        question_form = QuestionCreationForm()
    return render(request, 'questions/question_create.html', {'question_form': question_form, 'subject_id': subject_id,
                                                              'subject_slug': subject_slug})


@login_required
@require_http_methods(['GET', 'POST'])
def question(request, subject_id, subject_slug, question_id):
    # Check if a user is an author of subject or an author of a question
    if is_author_of_subject(request.user, subject_id) or is_author_of_question(request.user, question_id):
        # Question/answer deletion or answer ordinal number change
        if request.method == 'POST':

            if 'delete-question' in request.POST:
                try:
                    question_id = int(request.POST.get('delete-question'))
                    Question.objects.filter(id=question_id).delete()
                except Exception:
                    pass
                return redirect(Subject.objects.get(id=subject_id).get_absolute_url())

            elif 'delete-answer' in request.POST:
                try:
                    answer_id = int(request.POST.get('delete-answer'))
                    Answer.objects.filter(id=answer_id).delete()
                except Exception:
                    pass
                return redirect(Question.objects.get(id=question_id).get_absolute_url())

            elif 'up' in request.POST:
                answer_to_go_up = get_object_or_404(Answer, id=int(request.POST.get('up')))
                question = get_object_or_404(Question, id=question_id)
                answer_to_go_down = question.answers.filter(question=question, order__lt=answer_to_go_up.order) \
                    .order_by('-order').first()
                with transaction.atomic():
                    temp_order = answer_to_go_up.order
                    answer_to_go_up.order = answer_to_go_down.order
                    answer_to_go_down.order = temp_order
                    answer_to_go_up.save()
                    answer_to_go_down.save()
                return redirect(Question.objects.get(id=question_id).get_absolute_url())

            elif 'down' in request.POST:
                answer_to_go_down = get_object_or_404(Answer, id=int(request.POST.get('down')))
                question = get_object_or_404(Question, id=question_id)
                answer_to_go_up = question.answers.filter(question=question, order__gt=answer_to_go_down.order) \
                    .order_by('order').first()
                with transaction.atomic():
                    temp_order = answer_to_go_down.order
                    answer_to_go_down.order = answer_to_go_up.order
                    answer_to_go_up.order = temp_order
                    answer_to_go_down.save()
                    answer_to_go_up.save()
                return redirect(Question.objects.get(id=question_id).get_absolute_url())

        else:  # GET
            question = get_object_or_404(Question, id=question_id)
            answers = question.answers.all().order_by('order')
            return render(request, 'questions/question.html', {'question': question, 'answers': answers})

    else:
        return redirect(Subject.objects.get(id=subject_id).get_absolute_url())


@login_required
@require_http_methods(['GET', 'POST'])
def edit_question(request, subject_id, subject_slug, question_id):
    # Check if a user can edit a question
    if is_author_of_subject(request.user, subject_id) or is_author_of_question(request.user, question_id):
        if request.method == 'POST':
            question_form = QuestionCreationForm(data=request.POST)
            if question_form.is_valid():
                # new_question_edited = question_form.save(commit=False)
                question_edited = get_object_or_404(Question, id=question_id)
                question_edited.question = question_form.cleaned_data.get('question')

                # Remove tags
                for tag in question_edited.tags.all():
                    if tag.name not in re.split(', |,| ', question_form.data.get('tags')):
                        question_edited.tags.remove(tag)

                # Add tags
                for tag in re.split(', |,| ', question_form.data.get('tags')):
                    tag = tag.strip()
                    if tag != '':
                        question_edited.tags.add(tag)

                question_edited.save()

            return redirect(get_object_or_404(Question, id=question_id).get_absolute_url())

        else:
            question_edited = get_object_or_404(Question, id=question_id)
            question_form = QuestionCreationForm(initial={'question': question_edited.question,
                                                          'tags': question_edited.tags.all()})
            return render(request, 'questions/question_edit.html',
                          {'question_form': question_form, 'question': question_edited})

    else:
        return redirect(get_object_or_404(Subject, id=subject_id).get_absolute_url())


@login_required
@require_http_methods(['GET', 'POST'])
def add_answer(request, subject_id, subject_slug, question_id):
    # Check if a user can add an answer
    if is_author_of_subject(request.user, subject_id) or is_author_of_question(request.user, question_id):
        if request.method == 'POST':
            answer_form = AnswerCreationForm(data=request.POST)
            if answer_form.is_valid():
                new_answer = answer_form.save(commit=False)
                question = get_object_or_404(Question, id=question_id)
                ordinal_num = question.answers.all().order_by('-order').first().order + 1
                new_answer.question = question
                new_answer.order = ordinal_num
                new_answer.save()

            return redirect(get_object_or_404(Question, id=question_id).get_absolute_url())

        else:  # GET
            # Default value of order - next int
            question = get_object_or_404(Question, id=question_id)
            if question.answers.all():
                default_order = question.answers.all().order_by('order').last().order + 1
                answer_form = AnswerCreationForm(initial={'order': default_order})
            else:
                answer_form = AnswerCreationForm(initial={'order': 1})
            return render(request, 'questions/question_add_answer.html', {'answer_form': answer_form,
                                                                          'question': question})

    else:
        return redirect(get_object_or_404(Subject, id=subject_id).get_absolute_url())


@login_required
@require_http_methods(['GET', 'POST'])
def edit_answer(request, subject_id, subject_slug, question_id, answer_id):
    # Check if a user can edit an answer
    if is_author_of_subject(request.user, subject_id) or is_author_of_question(request.user, question_id):
        if request.method == 'POST':
            answer_form = AnswerCreationForm(data=request.POST)
            if answer_form.is_valid():
                # question = get_object_or_404(Question, id=question_id)
                answer_edited = get_object_or_404(Answer, id=answer_id)
                answer_edited.answer = answer_form.cleaned_data['answer']
                answer_edited.is_right = answer_form.cleaned_data['is_right']

                answer_edited.save()
                return redirect(get_object_or_404(Question, id=question_id).get_absolute_url())
                # else:
                #     # Return error to a template
                #     answer_form.add_error('order', 'Choose other ordinal number. '
                #                                    'This one has been already assigned to a different answer of this '
                #                                    'question.')
                #     return render(request, 'questions/question_edit_answer.html', {'answer_form': answer_form,
                #                                                                    'question': question})

        else:  # GET
            question = get_object_or_404(Question, id=question_id)
            answer_edited = get_object_or_404(Answer, id=answer_id)
            answer_form = AnswerCreationForm(initial={'answer': answer_edited.answer,
                                                      'is_right': answer_edited.is_right,
                                                      'order': answer_edited.order})
            return render(request, 'questions/question_edit_answer.html', {'answer_form': answer_form,
                                                                           'question': question})

    else:
        return redirect(get_object_or_404(Subject, id=subject_id).get_absolute_url())


@login_required
@require_http_methods(['GET', 'POST'])
def people(request, subject_id, subject_slug):
    subject = get_object_or_404(Subject, id=subject_id)
    if not is_author_of_subject(request.user, subject.id):
        return redirect(reverse('questions:subject', args=[subject_id, subject_slug]))

    if request.method == 'POST':
        # Remove owner from subject
        try:
            user_id = int(request.POST.get('delete'))

            user_to_be_removed = get_object_or_404(User, id=user_id)
            subject.ownership.remove(user_to_be_removed)
        except ValueError:
            pass

    # Subject owners without author
    owners = User.objects.filter(subjects__in=[subject]).exclude(id=subject.author.id).all()
    return render(request, 'questions/people.html', {'subject': subject, 'owners': owners})


@login_required
@require_http_methods(['GET', 'POST'])
def add_owner(request, subject_id, subject_slug):
    subject = get_object_or_404(Subject, id=subject_id)

    if not is_owner_of_subject(request.user, subject_id):
        return redirect(reverse('questions:subject', args=[subject.id, subject.slug]))

    if request.method == 'POST':
        # Add user to subject
        try:
            user_id = int(request.POST.get('user_id'))

            user_to_be_added = get_object_or_404(User, id=user_id)
            subject.ownership.add(user_to_be_added)
        except ValueError:
            pass

    # GET/POST
    users = User.objects.none()

    # Query search - usernames
    search_form = SearchForm()
    q = None
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            q = search_form.cleaned_data['query']

            # Trigram search
            owner_ids = User.objects.filter(subjects__in=[subject]).all().values_list('id', flat=True)
            users = User.objects.annotate(
                similarity=TrigramSimilarity('username', q)
            ).filter(similarity__gt=0.1).exclude(id__in=owner_ids).order_by('-similarity').all()

    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        # If page value is not int - get first page
        users_page = paginator.page(1)
    except EmptyPage:
        # If page value is bigger than the value of last page - get last page
        users_page = paginator.page(paginator.num_pages)

    return render(request, 'questions/people_add.html', {'subject': subject, 'users': users_page,
                                                         'query': q, 'search_form': search_form})
