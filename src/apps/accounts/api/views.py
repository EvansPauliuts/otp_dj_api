from core.permissions import CustomObjectPermissions
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import Permission
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.api.serializers import ChangePasswordSerializer
from apps.accounts.api.serializers import GroupSerializer
from apps.accounts.api.serializers import JobTitleSerializer
from apps.accounts.api.serializers import PermissionSerializer
from apps.accounts.api.serializers import ResetPasswordSerializer
from apps.accounts.api.serializers import TokenProvisionSerializer
from apps.accounts.api.serializers import UpdateEmailSerializer
from apps.accounts.api.serializers import UserFavoriteSerializer
from apps.accounts.api.serializers import UserSerializer
from apps.accounts.models import CustomGroup
from apps.accounts.models import JobTitle
from apps.accounts.models import Token
from apps.accounts.models import UserFavorite
from apps.accounts.permissions import OwnershipPermissions

User = get_user_model()


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = CustomGroup.objects.all()
    filterset_fields = ('name',)
    ordering_fields = '__all__'
    permission_classes = (CustomObjectPermissions,)


class PermissionViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    filterset_fields = ('name',)
    ordering_fields = '__all__'
    permission_classes = (CustomObjectPermissions,)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    search_fields = (
        'username',
        'email',
        'profiles__first_name',
        'profiles__last_name',
    )
    filterset_fields = (
        'is_active',
        'is_staff',
        'department__name',
        'username',
    )
    permission_classes = (OwnershipPermissions,)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = (
                self.queryset.filter(
                    organization_id=self.request.user.organization_id,
                )
                .select_related('profiles')
                .prefetch_related(
                    Prefetch('groups', queryset=CustomGroup.objects.only('id', 'name')),
                    Prefetch(
                        'user_permissions',
                        queryset=Permission.objects.only(
                            'id',
                            'name',
                            'content_type__app_label',
                            'codename',
                        ),
                    ),
                )
                .all()
            )
        else:
            queryset = (
                self.queryset.filter(
                    organization_id=self.request.user.organization_id,
                    organization=self.request.user.organization,
                    id=user.id,
                )
                .select_related('profiles')
                .prefetch_related(
                    Prefetch('groups', queryset=CustomGroup.objects.only('id', 'name')),
                    Prefetch(
                        'user_permissions',
                        queryset=Permission.objects.only(
                            'id',
                            'name',
                            'content_type__app_label',
                            'codename',
                        ),
                    ),
                )
                .all()
            )
        return queryset


class UpdatePasswordView(UpdateAPIView):
    throttle_scope = 'auth'
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            'Password updated successfully',
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(views.APIView):
    throttle_scope = 'auth'
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(request=request)
            return Response(
                {
                    'message': 'Password reset successfully. '
                    'Please check your email for new password',
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UpdateEmailView(views.APIView):
    throttle_scope = 'auth'
    serializer_class = UpdateEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save(request=request)
            return Response(
                {'message': 'Email successfully updated.'},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class JobTitleViewSet(viewsets.ModelViewSet):
    serializer_class = JobTitleSerializer
    queryset = JobTitle.objects.all()
    filterset_fields = ('status', 'name')
    search_fields = ('name', 'status')
    permission_classes = (CustomObjectPermissions,)

    def get_queryset(self):
        expand_users = self.request.query_params.get('expand_users', 'false')

        queryset = JobTitle.objects.filter(
            organization_id=self.request.user.organization_id,
        ).only(
            'id',
            'organization_id',
            'status',
            'description',
            'name',
            'job_function',
        )

        if expand_users.lower() == 'true':
            queryset = queryset.prefetch_related(
                Prefetch(
                    'profile__user',
                    queryset=User.objects.filter(
                        organization_id=self.request.user.organization_id,
                    ).only('username', 'organization_id'),
                ),
            )

        return queryset


class UserDetailView(views.APIView):
    permissions_classes = (IsAuthenticated,)
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        data = serializer.data
        return Response(
            {'result': data},
            status=status.HTTP_200_OK,
        )


class TokenProvisionView(ObtainAuthToken):
    throttle_scope = 'auth'
    permissions_classes = (AllowAny,)
    serializer_class = TokenProvisionSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        if token.is_expired:
            token.delete()
            Token.objects.create(user=user)

        if user.is_active:
            login(request, user)
            user.online = True
            user.last_login = timezone.now()
            user.session_key = request.session.session_key
            user.save()

        return Response(
            {'message': 'Login successfully'},
            status=status.HTTP_200_OK,
        )


class UserLogoutView(views.APIView):
    permission_classes = (AllowAny,)
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response(
                {'message': 'User is not logged in.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logout(request)
        user.online = False
        user.session_key = None
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveUserSessionView(views.APIView):
    permission_classes = IsAdminUser
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')

        if not user_id:
            raise exceptions.ValidationError({'user_id': 'This field is required.'})

        user = User.objects.get(pk__exact=user_id)

        if user.is_authenticated:
            logout(request)
            user.online = False
            user.session_key = None
            user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = UserFavoriteSerializer
    queryset = UserFavorite.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def delete(self, request, *args, **kwargs):
        page_id = request.data.get('page')
        if not page_id:
            return Response(
                {'error': 'Page ID is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_favorite = get_object_or_404(UserFavorite, user=request.user, page=page_id)
        user_favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
