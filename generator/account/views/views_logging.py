from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from account.forms import CustomLoginForm
from account.forms import CustomResetPasswordForm, CustomResetPasswordConfirmForm, CustomUserCreationForm


def main(request):
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    return render(request, 'base.html')


class CustomLoginView(LoginView):
    """
    Changes default authentication form to a custom one.
    Adds additional context - 'section'.
    """
    authentication_form = CustomLoginForm
    extra_context = {'section': 'login'}


class CustomResetPasswordView(PasswordResetView):
    form_class = CustomResetPasswordForm
    success_url = reverse_lazy('account:password_reset_done')


class CustomResetPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomResetPasswordConfirmForm
    success_url = reverse_lazy('account:password_reset_complete')


def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)  # Create now, do not save in database
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user})

    else:
        user_form = CustomUserCreationForm()
    return render(request, 'account/register.html', {'form': user_form, 'section': 'register'})
