from django.contrib.auth.models import User

# As for now it is not used (disabled in settings.py).
# In order to use it correctly we have to create a custom User model deriving from AbstractUser
# and email field must be defined as "unique".
# Later we have to set our model as default one (in settings).


class EmailAuthBackend:
    """
    Authentication of user based on email.
    """
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None

        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
