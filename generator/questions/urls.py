from django.urls import path
from . import views

app_name = 'questions'
urlpatterns = [
    path('subject/<int:subject_id>/<slug:subject_slug>/add-question/', views.create_question, name='question-create'),
    path('subject/<int:subject_id>/<slug:subject_slug>/edit', views.edit_subject, name='subject-edit'),
    path('subject/<int:subject_id>/<slug:subject_slug>/', views.subject, name='subject'),
    path('subject/create/', views.create_subject, name='subject-create'),
]
