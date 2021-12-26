from django.urls import path
from . import views

app_name = 'quiz'
urlpatterns = [
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/create/', views.create_quiz, name='create-quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/edit/',
         views.edit_quiz, name='edit-quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/tag/<slug:tag_slug>',
         views.quiz, name='quiz-questions-by-tag'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/<int:quiz_id>/<slug:quiz_slug>/',
         views.quiz, name='quiz'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/tag/<slug:tag_slug>/', views.quizzes, name='quiz-by-tag'),
    path('subject/<int:subject_id>/<slug:subject_slug>/tests/', views.quizzes, name='quizzes'),
]
