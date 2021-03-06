from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.forms import (AuthenticationForm,
                                       PasswordChangeForm,
                                       PasswordResetForm,
                                       SetPasswordForm,
                                       UserCreationForm)
from django.contrib.auth.models import User


class CustomLoginForm(AuthenticationForm):
    """
    Adds some classes to default AuthenticationForm fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'


class CustomChangePasswordForm(PasswordChangeForm):
    """
    Adds some classes to default PasswordChangeForm fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'


class CustomResetPasswordForm(PasswordResetForm):
    """
    Adds some classes to default PasswordResetForm fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'


class CustomResetPasswordConfirmForm(SetPasswordForm):
    """
    Adds some classes to default SetPasswordForm fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'


class CustomUserCreationForm(UserCreationForm):
    """
    Adds some classes to default UserCreationForm fields and decides which specific User model fields to show in a form.
    """
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(attrs={'data-theme': 'dark'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
