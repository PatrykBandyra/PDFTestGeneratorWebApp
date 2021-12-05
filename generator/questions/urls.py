from django.urls import path
from . import views

app_name = 'questions'
urlpatterns = [
    # Question and answers
    path('subject/<int:subject_id>/<slug:subject_slug>/<int:question_id>/', views.question, name='question'),
    path('subject/<int:subject_id>/<slug:subject_slug>/<int:question_id>/edit/',
         views.edit_question, name='question-edit'),
    path('subject/<int:subject_id>/<slug:subject_slug>/<int:question_id>/add-answer/',
         views.add_answer, name='question-add-answer'),
    path('subject/<int:subject_id>/<slug:subject_slug>/<int:question_id>/<int:answer_id>/edit-answer/',
         views.edit_answer, name='question-edit-answer'),
    path('subject/<int:subject_id>/<slug:subject_slug>/add-question/', views.create_question, name='question-create'),

    # Subject
    path('subject/<int:subject_id>/<slug:subject_slug>/edit', views.edit_subject, name='subject-edit'),
    # List of questions in subject
    path('subject/<int:subject_id>/<slug:subject_slug>/tag/<slug:tag_slug>/', views.subject, name='subject-by-tag'),
    path('subject/<int:subject_id>/<slug:subject_slug>/', views.subject, name='subject'),
    path('subject/create/', views.create_subject, name='subject-create'),
]
