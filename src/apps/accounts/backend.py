from django.contrib.auth.backends import ModelBackend
from models.account import UserA


class UserBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            user = (
                UserA._default_manager.only('id')
                .select_related('profile', 'organization')
                .get(pk__exact=user_id)
            )
        except UserA.DoesNotExist:
            return

        return user if self.user_can_authenticate(user) else None
