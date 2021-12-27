import re
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import TrigramSimilarity, SearchHeadline, SearchQuery, SearchVector, SearchRank
from django.db.models.functions import Greatest
from django.db import transaction
from django.urls import reverse
from questions.models import Subject, Question
from taggit.models import Tag
from django.db.models.query import QuerySet
from .forms import QuizCreationForm
from .utils import is_author_of_quiz
from .models import Quiz, QuizQuestion
from questions.utils import is_author_of_subject
from questions.forms import SearchForm, SearchTagForm


@login_required
@require_http_methods(['GET', 'POST'])
def quizzes(request, subject_id, subject_slug, tag_slug=None):
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

    # Query search - questions and answers
    search_form = SearchForm()
    query = None
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            # Trigram search
            quizzes = quizzes.annotate(
                similarity=Greatest(TrigramSimilarity('name', query), TrigramSimilarity('description', query))
            ).filter(similarity__gt=0.1).order_by('-similarity')

    # Query search - tags
    tag_search_form = SearchTagForm()
    tag_query = None
    if 'tag_query' in request.GET:
        tag_search_form = SearchTagForm(request.GET)
        if tag_search_form.is_valid():
            tag_query = tag_search_form.cleaned_data['tag_query']
            # Trigram search
            quizzes = quizzes.annotate(
                similarity=TrigramSimilarity('tags__name', tag_query)
            ).filter(similarity__gt=0.1).order_by('id', '-similarity').distinct('id')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        quizzes = quizzes.filter(tags__in=[tag])

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
                                                 'subject': subject,
                                                 'tag': tag, 'query': query,
                                                 'search_form': search_form,
                                                 'tag_query': tag_query,
                                                 'tag_search_form': tag_search_form})


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
            quiz_form.save_m2m()
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
                tag = tag.strip()
                if tag != '':
                    quiz.tags.add(tag)

            quiz.save()

            ret = request.GET.get('ret')
            if ret:
                return redirect(ret)

            return redirect(reverse('quiz:quizzes', args=[subject_id, subject_slug]))
    else:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        subject = get_object_or_404(Subject, id=subject_id)
        quiz_form = QuizCreationForm(instance=quiz)

        ret = request.GET.get('ret')

        return render(request, 'quiz/quiz_create.html', {'quiz_form': quiz_form, 'section': 'edit_quiz',
                                                         'quiz': quiz, 'subject': subject, 'ret': ret})


@login_required
@require_http_methods(['GET', 'POST'])
def quiz(request, subject_id, subject_slug, quiz_id, quiz_slug, tag_slug=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Remove question from
    if request.method == 'POST':

        # Quiz deletion
        quiz_to_delete_id = request.POST.get('delete_quiz')
        if quiz_to_delete_id:
            try:
                quiz_to_delete_id = int(quiz_to_delete_id)
                # Check if user is an author of a quiz or an author of a subject - only those can delete a quiz
                if not is_author_of_quiz(request.user, quiz_to_delete_id) and \
                        not is_author_of_subject(request.user, subject_id):
                    raise Exception

                Quiz.objects.get(id=quiz_to_delete_id).delete()

                return redirect(reverse('quiz:quizzes', args=[subject_id, subject_slug]))

            except Exception:
                return redirect(reverse('quiz:quizzes', args=[subject_id, subject_slug]))

        # Remove question from test
        question_id = request.POST.get('delete')
        if question_id:
            try:
                # Check if user is an author of a subject or an author of a quiz
                question_id = int(request.POST.get('delete'))
                if not is_author_of_quiz(request.user, question_id) and \
                        not is_author_of_subject(request.user, subject_id):
                    raise Exception

                QuizQuestion.objects.filter(quiz_id=quiz.id, question_id=question_id).delete()
            except Exception:
                pass

        if 'up' in request.POST:
            question_to_go_up = get_object_or_404(Question, id=int(request.POST.get('up')))
            quiz = get_object_or_404(Quiz, id=quiz_id)

            # Check rights to modify order
            if not is_author_of_quiz(request.user, question_id) and \
                    not is_author_of_subject(request.user, subject_id):
                return redirect(reverse('quiz:quiz', args=[subject_id, subject_slug, quiz_id, quiz_slug]))

            quiz_question_to_go_up = QuizQuestion.objects.get(quiz_id=quiz.id, question_id=question_to_go_up.id)
            quiz_question_to_go_down = QuizQuestion.objects.filter(quiz_id=quiz.id,
                                                                   order__lt=quiz_question_to_go_up.order) \
                .order_by('-order').first()

            with transaction.atomic():
                temp_order = quiz_question_to_go_up.order
                quiz_question_to_go_up.order = quiz_question_to_go_down.order
                quiz_question_to_go_down.order = temp_order
                quiz_question_to_go_up.save()
                quiz_question_to_go_down.save()
            return redirect(reverse('quiz:quiz', args=[subject_id, subject_slug, quiz_id, quiz_slug]))

        elif 'down' in request.POST:
            question_to_go_down = get_object_or_404(Question, id=int(request.POST.get('down')))
            quiz = get_object_or_404(Quiz, id=quiz_id)

            # Check rights to modify order
            if not is_author_of_quiz(request.user, question_id) and \
                    not is_author_of_subject(request.user, subject_id):
                return redirect(reverse('quiz:quiz', args=[subject_id, subject_slug, quiz_id, quiz_slug]))

            quiz_question_to_go_down = QuizQuestion.objects.get(quiz_id=quiz.id, question_id=question_to_go_down.id)
            quiz_question_to_go_up = QuizQuestion.objects.filter(quiz_id=quiz.id,
                                                                 order__gt=quiz_question_to_go_down.order) \
                .order_by('order').first()

            with transaction.atomic():
                temp_order = quiz_question_to_go_down.order
                quiz_question_to_go_down.order = quiz_question_to_go_up.order
                quiz_question_to_go_up.order = temp_order
                quiz_question_to_go_down.save()
                quiz_question_to_go_up.save()
            return redirect(reverse('quiz:quiz', args=[subject_id, subject_slug, quiz_id, quiz_slug]))

        # Randomize question order
        randomize = request.POST.get('randomize')
        if randomize == 'yes':
            quiz_questions = QuizQuestion.objects.filter(quiz_id=quiz.id).all()
            questions_order = [qq.order for qq in quiz_questions]
            random.shuffle(questions_order)
            with transaction.atomic():
                for qq, order in zip(quiz_questions, questions_order):
                    qq.order = order
                    qq.save()

    # GET/POST
    quiz_questions = quiz.quiz_questions.order_by('-order').all()
    questions_ids = [quiz_question.question.id for quiz_question in quiz_questions]

    questions = Question.objects.filter(id__in=questions_ids).order_by('question_quizzes__order').all()

    # Query search - questions and answers
    search_form = SearchForm()
    q = None
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            q = search_form.cleaned_data['query']
            # Trigram search
            # questions = questions.annotate(
            #     similarity=Greatest(TrigramSimilarity('question', query), TrigramSimilarity('answers__answer', query))
            # ).filter(similarity__gt=0.1).order_by('-similarity')

            # Rank search
            vector = SearchVector('question', 'answers__answer')
            query = SearchQuery(q)
            questions = questions.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank')\
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
        # If page value is bigger than the value of last page - get last page
        questions_page = paginator.page(paginator.num_pages)

    return render(request, 'quiz/quiz.html', {'quiz': quiz,
                                              'subject': quiz.subject,
                                              'questions': questions_page,
                                              'tag': tag, 'query': q,
                                              'search_form': search_form,
                                              'tag_query': tag_query,
                                              'tag_search_form': tag_search_form})
