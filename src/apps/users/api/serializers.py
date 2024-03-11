from datetime import UTC, datetime

from django.db import transaction
from rest_framework import exceptions, serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.tasks import send_phone_notification
from apps.users.utils import clean_phone, generate_otp, is_admin_user
from apps.users.common import TokenEnum
from apps.users.models import User, Token, FileModel, ImageModel, PendingUser

class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'firstname',
            'lastname',
            'email',
            'image',
            'verified',
            'created_at',
            'roles',
        )
        extra_kwargs = {
            'verified': {
                'read_only': True,
            },
            'roles': {
                'read_only': True,
            },
        }

    def to_representation(self, instance):
        return super().to_representation(instance)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'firstname',
            'lastname',
            'image',
            'verified',
            'roles',
        )
        extra_kwargs = {
            'last_login': {
                'read_only': True,
            },
            'verified': {
                'read_only': True,
            },
            'roles': {
                'required': False,
            },
        }

    def validate(self, attrs):
        auth_user = self.context['request'].user
        new_role_assignment = attrs.get('roles', None)

        if new_role_assignment and is_admin_user(auth_user):
            pass
        else:
            attrs.pop('roles', None)

        return super().validate(attrs)

    def update(self, instance, validated_data):
        if validated_data.get('password', False):
            validated_data.pop('password')
        return super().update(instance, validated_data)


class OnboardUserSerializer(serializers.Serializer):
    phone = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    password = serializers.CharField(
        max_length=12,
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        strip_number = phone.lower().strip()
        cleaned_number = clean_phone(strip_number)

        if get_user_model().objects.filter(phone__iexact=cleaned_number).exists():
            raise serializers.ValidationError(
                {'phone': 'Phone number already exists'},
            )
        attrs['phone'] = cleaned_number
        return super().validate(attrs)

    def create(self, validated_data: dict):
        otp = generate_otp()
        phone_number = validated_data.get('phone')

        user, _ = PendingUser.objects.update_or_create(
            phone=phone_number,
            defaults={
                'phone': phone_number,
                'verification_code': otp,
                'password': make_password(validated_data.get('password')),
                'created': datetime.now(UTC),
            },
        )

        message_info = {
            'message': f'Account Verification!\nYour OTP for BotoApp is {otp}.\n'
            f'It expires in 10 minutes',
            'phone': user.phone,
        }

        send_phone_notification.delay(message_info)
        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
    )


class AccountVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(
        required=True,
    )
    phone = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    def validate(self, attrs: dict):
        phone_number: str = attrs.get('phone').strip().lower()
        mobile: str = clean_phone(phone_number)

        pending_user: PendingUser = PendingUser.objects.filter(
            phone=mobile,
            verification_code=attrs.get('otp'),
        ).first()

        if pending_user and pending_user.is_valid():
            attrs['phone'] = mobile
            attrs['password'] = pending_user.password
            attrs['pending_user'] = pending_user
        else:
            raise serializers.ValidationError(
                {'otp': 'Verification failed. Invalid OTP or Number'},
            )

        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('otp')
        pending_user = validated_data.pop('pending_user')

        User.objects.create_user_with_phone(**validated_data)
        pending_user.delete()

        return validated_data


class InitiatePasswordResetSerializer(serializers.Serializer):
    phone = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    def validate(self, attrs: dict):
        phone = attrs.get('phone')
        strip_number = phone.lower().strip()
        mobile = clean_phone(strip_number)
        user = get_user_model().objects.filter(phone=mobile, is_active=True).first()

        if not user:
            raise serializers.ValidationError(
                {
                    'phone': 'Phone number not registered.',
                },
            )

        attrs['phone'] = mobile
        attrs['user'] = user

        return super().validate(attrs)

    def create(self, validated_data):
        phone = validated_data.get('phone')
        user = validated_data.get('user')
        otp = generate_otp()

        token, _ = Token.objects.update_or_create(
            user=user,
            token_type=TokenEnum.PASSWORD_RESET,
            defaults={
                'user': user,
                'token_type': TokenEnum.PASSWORD_RESET,
                'token': otp,
                'created': datetime.now(UTC),
            },
        )

        message_info = {
            'message': f'Password Reset!\nUse {otp} to reset your '
            f'password.\nIt expires in 10 minutes',
            'phone': phone,
        }

        send_phone_notification.delay(message_info)
        return token


class CreatePasswordFromResetOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        access_token = refresh.access_token
        self.user.save_last_login()

        data['refresh'] = str(refresh)
        data['access'] = str(access_token)

        return data

    @classmethod
    def get_token(cls, user: User):
        if not user.verified:
            raise exceptions.AuthenticationFailed(
                'Account not verified.',
                code='authentication',
            )
        token = super().get_token(user)
        token.id = user.id

        token['firstname'] = user.firstname
        token['lastname'] = user.lastname
        token['email'] = user.email
        token['roles'] = user.roles

        return token


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=128,
        required=False,
    )
    new_password = serializers.CharField(
        max_length=128,
        min_length=5,
    )

    def validate_old_password(self, value):
        request = self.context['request']

        if not request.user.check_password(value):
            raise serializers.ValidationError(
                'Old password is incorrect.',
            )
        return value

    def save(self):
        user: User = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)

        user.save(update_fields=['password'])


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            user = authenticate(
                request=self.context.get('request'),
                username=email.lower().strip(),
                password=password,
            )

        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(
                msg,
                code='authentication',
            )

        attrs['user'] = user
        return attrs


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = '__all__'


class MultiFileSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
    )


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = '__all__'


class MultiImageSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
    )
