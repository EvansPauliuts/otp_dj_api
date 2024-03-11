from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from core.utils.serializers import GenericModelSerializer
from django.contrib.auth.models import Group, Permission

from apps.accounts import tasks
from apps.accounts.models import (
    User,
    Token,
    JobTitle,
    UserProfile,
    Organization,
    UserFavorite,
)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class JobTitleListingField(serializers.RelatedField):
    def to_representation(self, instance):
        return instance.name


class UserProfileSerializer(GenericModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
    )
    job_title = serializers.PrimaryKeyRelatedField(
        queryset=JobTitle.objects.all(),
        required=False,
        allow_null=True,
    )
    title_name = JobTitleListingField(
        source='title',
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = (
            'organization',
            'business_unit',
            'id',
            'user',
        )
        extra_kwargs = {
            'organization': {
                'required': False,
            },
            'business_unit': {
                'required': False,
            },
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'User Request',
            summary='User Request',
            value={
                'id': 'b08e6e3f-28da-47cf-ad48-99fc7919c087',
                'department': '7eaaca59-7e58-4398-82e9-d6d9321d483d',
                'username': 'test_user',
                'email': 'test_user@example.com',
                'password': 'test_password',
                'profile': {
                    'id': 'a75a4b66-3f3a-48af-a089-4b7f1373f7a1',
                    'user': 'b08e6e3f-28da-47cf-ad48-99fc7919c087',
                    'job_title': 'bfa74d30-915f-425a-b957-15b826c3bee2',
                    'first_name': 'Example',
                    'last_name': 'User',
                    'profile_picture': None,
                    'address_line_1': '123 Example Location',
                    'address_line_2': 'Unit 123',
                    'city': 'San Antonio',
                    'state': 'TX',
                    'zip_code': '12345',
                    'phone': '12345678903',
                },
            },
            response_only=True,
        ),
        OpenApiExample(
            'User Response',
            summary='User Response',
            value={
                'last_login': '2023-01-26T19:17:37.565110Z',
                'is_superuser': False,
                'id': 'b08e6e3f-28da-47cf-ad48-99fc7919c087',
                'department': '7eaaca59-7e58-4398-82e9-d6d9321d483d',
                'username': 'test_user',
                'email': 'test_user@example.com',
                'is_staff': False,
                'date_joined': '2022-12-04T00:05:00Z',
                'groups': [
                    0,
                ],
                'user_permissions': [
                    0,
                ],
                'profile': {
                    'id': 'a75a4b66-3f3a-48af-a089-4b7f1373f7a1',
                    'user': 'b08e6e3f-28da-47cf-ad48-99fc7919c087',
                    'job_title': 'bfa74d30-915f-425a-b957-15b826c3bee2',
                    'first_name': 'Example',
                    'last_name': 'User',
                    'profile_picture': 'http://localhost:8000/media/'
                    'profile_pictures/placeholder.png',
                    'address_line_1': '123 Example Location',
                    'address_line_2': 'Unit 123',
                    'city': 'San Antonio',
                    'state': 'TX',
                    'zip_code': '12345',
                    'phone': '12345678903',
                },
            },
            response_only=True,
        ),
    ],
)
class UserSerializer(GenericModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    user_permissions = serializers.SerializerMethodField()
    profile = UserProfileSerializer(required=False)
    full_name = serializers.CharField(
        source='profile.get_full_name',
        read_only=True,
    )

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = (
            'id',
            'online',
            'last_login',
            'groups',
            'user_permissions',
            'organization',
            'business_unit',
            'is_staff',
            'is_active',
            'is_superuser',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'date_joined': {'read_only': True},
            'organization': {'required': False},
            'business_unit': {'required': False},
        }

    def get_user_permissions(self, obj):
        permissions = set()
        for group in obj.groups.all():
            permissions.update(group.permissions.values_list('codename', flat=True))
        return list(permissions)

    def create(self, validated_data):
        organization = super().get_organization
        validated_data['organization'] = organization

        business_unit = super().get_business_unit
        validated_data['business_unit'] = business_unit

        if validated_data.pop('password', None):
            raise serializers.ValidationError(
                {
                    'password': 'Password cannot be added directly to a user. '
                    'Please use the password reset endpoint.',
                },
            )

        profile_data = validated_data.pop('profile', {})
        profile_data['organization'] = organization
        profile_data['business_unit'] = business_unit

        new_password = User.objects.make_random_password()
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=new_password,
            organization=organization,
            business_unit=business_unit,
        )

        UserProfile.objects.create(user=user, **profile_data)

        if profile_data.get('profile_picture'):
            transaction.on_commit(
                lambda: tasks.generate_thumbnail_task.delay(user.profile.id),
            )

        return user

    def update(self, instance, validated_data):
        if validated_data.pop('password', None):
            raise serializers.ValidationError(
                'Password cannot be changed using this endpoint. '
                'Please use the change password endpoint.',
            )

        if profile_data := validated_data.pop('profile', None):
            instance.profile.update_profile(**profile_data)

        instance.update_user(**validated_data)
        return instance


class MinimalUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile')


class JobTitleSerializer(GenericModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = JobTitle
        fields = (
            'id',
            # 'organization_id',
            'status',
            'description',
            'name',
            'job_function',
            'users',
        )

    def validate_name(self, value):
        organization = super().get_organization
        queryset = JobTitle.objects.filter(
            organization=organization,
            name__iexact=value,
        )

        if self.instance and isinstance(self.instance, JobTitle):
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                'Job Title with this `name` already exists. Please try again.',
            )
        return value

    def get_users(self, obj):
        expand_users = self.context['request'].query_params.get('expand_users', 'false')
        if expand_users.lower() != 'true':
            return []
        return [profile.user.username for profile in obj.profile.all()]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        expand_users = self.context['request'].query_params.get('expand_users', 'false')
        if expand_users.lower() != 'true':
            ret.pop('users', None)
        return ret


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Change User Password Response',
            summary='Change User Password Response',
            value={'Password updated successfully.'},
            response_only=True,
            status_codes=['200'],
        ),
    ],
)
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Old password is incorrect. Please try again.',
            )
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(
                'Passwords do not match. Please try again.',
            )
        password_validation.validate_password(
            attrs['new_password'],
            self.context['request'].user,
        )
        return attrs

    def save(self, request):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist as e:
            raise serializers.ValidationError(
                'No user found with the given email exists. Please try again.',
            ) from e

        if not user.is_active:
            raise serializers.ValidationError(
                'This user is not active. Please try again.',
            )
        return value

    def save(self, request):
        user = User.objects.get(email=self.validated_data['email'])
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()

        return user


class UpdateEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        email = attrs.get('email')

        user = self.context['request'].user

        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {
                    'current_password': 'Current password is incorrect. Please try again.',
                },
            )

        if user.email == email:
            raise serializers.ValidationError(
                {
                    'email': 'New email cannot be the same as the current email.',
                },
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'A user with this email already exists.'},
            )

        return attrs

    def save(self, request):
        user = self.context['request'].user
        user.email = self.validated_data['email']
        user.save()
        return user


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('token')

        if Token.objects.filter(key=token).exists():
            return attrs
        raise serializers.ValidationError(
            'Unable to validate given token. Please try again.',
            code='authentication',
        )


class TokenSerializer(serializers.ModelSerializer):
    key = serializers.CharField(
        min_length=40,
        max_length=40,
        allow_blank=True,
        required=False,
    )
    user = UserSerializer()

    class Meta:
        model = Token
        fields = (
            'id',
            'user',
            'created',
            'expires',
            'last_used',
            'key',
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Token Provision Request',
            summary='Token Provision request',
            value={
                'username': 'test',
                'password': 'test',
            },
            response_only=True,
        ),
        OpenApiExample(
            'Token Provision Response',
            summary='Token Provision Response',
            value={
                'user_id': 'b08e6e3f-28da-47cf-ad48-99fc7919c087',
                'api_token': '756ab1e4e0d23ff3a7eda30e09ffda65cae2d623',
            },
            response_only=True,
        ),
    ],
)
class TokenProvisionSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError(
                {'username': 'Username does not exist. Please try again.'},
                code='username_not_found',
            ) from exc

        auth_user = authenticate(username=username, password=password)

        if auth_user is None:
            raise serializers.ValidationError(
                {'password': 'Password is incorrect. Please try again.'},
                code='incorrect_password',
            )

        attrs['user'] = auth_user
        return attrs


class UserFavoriteSerializer(GenericModelSerializer):
    class Meta:
        model = UserFavorite
        fields = (
            'id',
            'user',
            'page',
            'created',
        )
        extra_kwargs = {
            'organization': {'required': False},
            'business_unit': {'required': False},
            'user': {'required': False},
        }

    def create(self, validated_data):
        organization = super().get_organization
        validated_data['organization'] = organization

        business_unit = super().get_business_unit
        validated_data['business_unit'] = business_unit

        validated_data['user'] = self.context['request'].user

        return UserFavorite.objects.create(
            user=validated_data['user'],
            page=validated_data['page'],
            organization=organization,
            business_unit=business_unit,
        )
