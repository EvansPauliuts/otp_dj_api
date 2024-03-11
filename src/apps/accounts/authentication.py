from django.utils import timezone
from rest_framework import HTTP_HEADER_ENCODING, exceptions, authentication

from apps.accounts.models.account import Token

def get_authorization_header(request):
    auth = request.headers.get('authorization', b'')
    if isinstance(auth, str):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class BearerTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'
    model = Token

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if auth and auth[0].lower() == self.keyword.lower().encode():
            if len(auth) == 1:
                raise exceptions.AuthenticationFailed(
                    'Invalid token header. No credentials provided. Please login again.',
                )
            if len(auth) > 2:
                raise exceptions.AuthenticationFailed(
                    'Invalid token header. Token string should '
                    'not contain spaces. Please login again.',
                )

            try:
                token = auth[1].decode()
            except UnicodeError as e:
                raise exceptions.AuthenticationFailed(
                    'Invalid token header. Token string should not contain invalid characters.',
                ) from e
        else:
            token = request.COOKIES.get('auth_token')
            if not token:
                return None
        return self.authenticate_credentials(key=token)

    def authenticate_credentials(self, key):
        try:
            token = (
                self.model.objects.select_related('user')
                .only(
                    'user_id',
                    'user__is_active',
                    'user__organization_id',
                    'key',
                    'expires',
                    'last_used',
                )
                .get(key=key)
            )
        except self.model.DoesNotExist as e:
            raise exceptions.AuthenticationFailed('Invalid token.') from e

        self.validate_token(token=token)
        return token.user, token

    @staticmethod
    def validate_token(token):
        if not token.last_used or (timezone.now() - token.last_used).total_seconds() > 60:
            token.last_used = timezone.now()
            token.save(update_fields=['last_used'])

        if token.is_expired and token.expires:
            raise exceptions.AuthenticationFailed(
                f"Token expired at {token.expires.strftime('%Y-%m-%d %H:%M:%S')}."
                f" Please login again.",
            )

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted. Please login again.')
