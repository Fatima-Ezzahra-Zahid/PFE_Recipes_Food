from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Attempt to find a user with the given email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        # Check if the password is correct
        if user.check_password(password):
            return user
        return None
