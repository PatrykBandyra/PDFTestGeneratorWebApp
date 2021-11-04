from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from questions.models import Subject

from account.forms import CustomChangePasswordForm


@login_required
def dashboard(request):
    # Subject deletion
    if request.method == 'POST':
        try:
            subject_id = int(request.POST.get('delete'))
            Subject.objects.filter(id=subject_id).delete()
        except Exception:
            pass

    subjects = Subject.objects.filter(ownership=request.user)
    authorial_subjects = Subject.objects.filter(author=request.user)
    return render(request, 'account/dashboard.html',
                  {'section': 'dashboard', 'subjects': subjects, 'authorial_subjects': authorial_subjects})


class CustomChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomChangePasswordForm
