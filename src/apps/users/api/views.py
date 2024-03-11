from core.permissions import AllowAny
from core.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import inline_serializer
from rest_framework import filters
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.common import TokenEnum
from apps.users.filters import UserFilter
from apps.users.models import FileModel
from apps.users.models import ImageModel
from apps.users.models import Token
from apps.users.models import User
from apps.users.utils import IsAdmin
from apps.users.utils import delete_cache
from apps.users.utils import is_admin_user

from .serializers import AccountVerificationSerializer
from .serializers import AuthTokenSerializer
from .serializers import CreatePasswordFromResetOTPSerializer
from .serializers import CustomObtainTokenPairSerializer
from .serializers import EmailSerializer
from .serializers import FileSerializer
from .serializers import ImageSerializer
from .serializers import InitiatePasswordResetSerializer
from .serializers import ListUserSerializer
from .serializers import MultiFileSerializer
from .serializers import MultiImageSerializer
from .serializers import OnboardUserSerializer
from .serializers import PasswordChangeSerializer
from .serializers import UpdateUserSerializer


class CustomObtainTokenPairView(TokenObtainPairView):
    serializer_class = CustomObtainTokenPairSerializer


class UserViewSets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = UserFilter
    search_fields = (
        'email',
        'firstname',
        'lastname',
        'phone',
    )
    ordering_fields = (
        'created_at',
        'email',
        'firstname',
        'lastname',
        'phone',
    )
    CACHE_KEY_PREFIX = 'user-view'

    def get_queryset(self):
        user = self.request.user

        if is_admin_user(user):
            return super().get_queryset().all()
        return super().get_queryset().filter(id=user.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return OnboardUserSerializer
        if self.action in ('partial_update', 'update'):
            return UpdateUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permissions_classes = self.permission_classes

        if self.action == 'create':
            permissions_classes = (AllowAny,)
        elif self.action in ('list', 'retrieve', 'partial_update', 'update'):
            permissions_classes = (IsAuthenticated,)
        elif self.action == 'destroy':
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
            ),
        },
        description='Sign Up witha validate phone number',
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        delete_cache(self.CACHE_KEY_PREFIX)
        return Response(
            {'success': True, 'message': 'OTP sent for verification!'},
            status=status.HTTP_200_OK,
        )

    @method_decorator(
        cache_page(20, key_prefix=CACHE_KEY_PREFIX),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
            token=request.data['otp'],
            token_type=TokenEnum.PASSWORD_RESET,
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
                        default='Account Verification Successful',
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
        except Exception as e:  # noqa: BLE001
            return Response(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileViewSet(viewsets.ModelViewSet):
    queryset = FileModel.objects.all()
    serializer_class = FileSerializer

    @action(
        methods=['POST'],
        detail=False,
    )
    def single_upload(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        FileModel.objects.create(file=file)

        return Response(
            {'success': True, 'message': 'File successfully uploaded!'},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['POST'],
        detail=False,
    )
    def multiple_files(self, request, *args, **kwargs):
        serializer = MultiFileSerializer(data=request.data or None)
        serializer.is_valid(raise_exception=True)
        files = serializer.validated_data['files']

        files_list = [FileModel(file=file) for file in files]

        if files_list:
            FileModel.objects.bulk_create(files_list)

        return Response(
            {'message': 'Multiple files uploaded!'},
            status=status.HTTP_200_OK,
        )


class ImageViewSet(viewsets.ModelViewSet):
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer

    @action(
        methods=['POST'],
        detail=False,
    )
    def multiple_upload(self, request, *args, **kwargs):
        serializer = MultiImageSerializer(data=request.data or None)
        serializer.is_valid(raise_exception=True)
        images = serializer.validated_data['images']

        images_list = [ImageModel(file=image) for image in images]

        if images_list:
            ImageModel.objects.bulk_create(images_list)

        return Response(
            {'message': 'Multiple images uploaded!'},
            status=status.HTTP_200_OK,
        )
