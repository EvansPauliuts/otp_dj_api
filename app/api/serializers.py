from datetime import datetime, timezone

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction

from api.models import PendingUser
from .utils import is_admin_user, generate_otp, clean_phone
from .tasks import send_phone_notification


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
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
        model = get_user_model()
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
        instance = super().update(instance, validated_data)
        return instance


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
                'created_at': datetime.now(timezone.utc),
            },
        )

        message_info = {
            'message': f'Account Verification!\nYour OTP for BotoApp is {otp}.\nIt expires in 10 minutes',
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
    def create(self, validated_data: dict):
        validated_data.pop('otp')
        pending_user = validated_data.pop('pending_user')

        User.objects.create_user_with_phone(**validated_data)
        pending_user.delete()

        return validated_data
