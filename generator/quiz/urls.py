from django.urls import path
from . import views

app_name = 'quiz'
urlpatterns = [
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/create/', views.create_quiz, name='create-quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/edit/',
         views.edit_quiz, name='edit-quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/tag/<slug:tag_slug>',
         views.quiz, name='quiz-questions-by-tag'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/add-question/tag/<slug:tag_slug>/',
         views.add_question_to_quiz, name='add-question-to-quiz-by-tag'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/add-question/',
         views.add_question_to_quiz, name='add-question-to-quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/',
         views.quiz, name='quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/pdf/',
         views.quiz_pdf, name='quiz-pdf'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/tag/<slug:tag_slug>/', views.quizzes, name='quiz-by-tag'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/', views.quizzes, name='quizzes'),
]
