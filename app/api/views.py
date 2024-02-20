from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import (
    ListUserSerializer,
    UpdateUserSerializer,
    OnboardUserSerializer,
    EmailSerializer,
    AccountVerificationSerializer,
    InitiatePasswordResetSerializer,
    CreatePasswordFromResetOTPSerializer,
    PasswordChangeSerializer,
    CustomObtainTokenPairSerializer,
    AuthTokenSerializer,
)
from .utils import is_admin_user, IsAdmin
from .models import Token
from .enums import TokenEnum


class CustomObtainTokenPairView(TokenObtainPairView):
    serializer_class = CustomObtainTokenPairSerializer


class UserViewSets(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = ListUserSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('GET', 'POST', 'PATCH', 'DELETE')

    def get_queryset(self):
        user = self.request.user

        if is_admin_user(user):
            return super().get_queryset().all()
        return super().get_queryset().filter(id=user.id)

    def get_serializer_class(self):
        if self.action in ('create',):
            return OnboardUserSerializer
        if self.action in ('partial_update', 'update'):
            return UpdateUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permissions_classes = self.permission_classes

        if self.action in ('create',):
            permissions_classes = (AllowAny,)
        elif self.action in ('list', 'retrieve', 'partial_update', 'update'):
            permissions_classes = (IsAuthenticated,)
        elif self.action in ('destroy',):
            permissions_classes = (IsAdmin,)

        return [permission() for permission in permissions_classes]

    @extend_schema(
        responses={
            200: inline_serializer(
                name='VerificationStatus',
                fields={
                    'success': serializers.BooleanField(default=True),
                    'message': serializers.CharField(
                        default='OTP sent for verification',
                    ),
                },
            )
        },
        description='Sign Up witha validate phone number',
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'success': True, 'message': 'OTP sent for verification!'},
            status=status.HTTP_200_OK,
        )


class AuthViewSets(viewsets.GenericViewSet):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in (
            'initiate_password_reset',
            'create_password',
            'verify_account',
        ):
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(
        methods=['POST'],
        detail=False,
        serializer_class=InitiatePasswordResetSerializer,
        url_path='initiate-password-reset',
    )
    def initiate_password_reset(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'success': True, 'message': 'Temporary password sent to your mobile!'},
            status=200,
        )

    @action(
        methods=['POST'],
        detail=False,
        serializer_class=CreatePasswordFromResetOTPSerializer,
        url_path='create-password',
    )
    def create_password(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token: Token = Token.objects.filter(
            token=request.data['otp'], token_type=TokenEnum.PASSWORD_RESET
        ).first()

        if not token or not token.is_valid():
            return Response(
                {'success': False, 'errors': 'Invalid password reset otp'},
                status=400,
            )

        token.reset_user_password(
            request.data['new_password'],
        )
        token.delete()

        return Response(
            {'success': True, 'message': 'Password successfully reset'},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name='AccountVerificationStatus',
                fields={
                    'success': serializers.BooleanField(default=True),
                    'message': serializers.CharField(
                        default='Account Verification Successful'
                    ),
                },
            ),
        },
    )
    @action(
        methods=['POST'],
        detail=False,
        serializer_class=AccountVerificationSerializer,
        url_path='verify-account',
    )
    def verify_account(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'success': True, 'message': 'Account Verification Successful'},
            status=200,
        )


class PasswordChangeView(viewsets.GenericViewSet):
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        context = {'request': request}
        serializer = self.get_serializer(
            data=request.data,
            context=context,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Your password has been updated.'},
            status.HTTP_200_OK,
        )


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        try:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'token': token.key,
                    'created': created,
                    'roles': user.roles,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
