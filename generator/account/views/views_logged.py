from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render
from questions.models import Subject

from account.forms import CustomChangePasswordForm


@login_required
def dashboard(request):
    subjects = Subject.objects.filter(ownership=request.user.id)
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'subjects': subjects})


class CustomChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomChangePasswordForm
