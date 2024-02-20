from django.contrib.auth.base_user import BaseUserManager
from .enums import SystemRoleEnum


class CustomUserManager(BaseUserManager):
    def create_user_with_phone(self, phone, **extra_fields):
        if not phone:
            raise ValueError('Phone must be set')
        user = self.model(
            phone=phone,
            is_active=True,
            verified=True,
            roles=[
                SystemRoleEnum.CUSTOMER,
            ],
            **extra_fields
        )
        user.save()
        return user

    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('Phone must be set')

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(phone, password, **extra_fields)
        user.roles = [
            SystemRoleEnum.ADMIN,
        ]

        user.save()
