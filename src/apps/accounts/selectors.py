from django.contrib.auth import get_user_model

from apps.accounts.models import Token

User = get_user_model()


def get_users_by_organization_id(*, organization_id):
    try:
        return User.objects.filter(organization_id=organization_id)
    except User.DoesNotExist:
        return None


def get_user_auth_token_from_request(*, request):
    token, _ = Token.objects.get_or_create(user=request.user)
    return token.key
