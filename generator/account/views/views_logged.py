from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render

from account.forms import CustomChangePasswordForm


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


class CustomChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomChangePasswordForm
