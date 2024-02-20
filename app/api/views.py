from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from .serializers import ListUserSerializer, UpdateUserSerializer, OnboardUserSerializer
from .utils import is_admin_user, IsAdmin


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
