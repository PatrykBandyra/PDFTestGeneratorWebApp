from django.urls import path
from . import views

app_name = 'questions'
urlpatterns = [
    path('<int:user_id>/<slug:subject_name>', views.subject, name='subject'),
]