from models.account import User
from django.contrib.auth.backends import ModelBackend


class UserBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            user = (
                User._default_manager.only('id')
                .select_related('profile', 'organization')
                .get(pk__exact=user_id)
            )
        except User.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
