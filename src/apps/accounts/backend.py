from django.contrib.auth.backends import ModelBackend
from models.account import User


class UserBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            user = (
                User._default_manager.only('id')  # noqa: SLF001
                .select_related('profile', 'organization')
                .get(pk__exact=user_id)
            )
        except User.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
