from django.urls import path
from . import views

app_name = 'questions'
urlpatterns = [
    path('subject/create/', views.create_subject, name='subject-create'),
    path('subject/<int:subject_id>/<slug:subject_slug>/edit', views.edit_subject, name='subject-edit'),
    path('seubject/<int:subject_id>/<slug:subject_slug>/', views.subject, name='subject'),
]
