from apps.accounts.models import Token
from django.utils.functional import cached_property
from rest_framework import serializers


class GenericModelSerializer(serializers.ModelSerializer):
    @cached_property
    def get_organization(self):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.organization

        token = request.headers.get('authorization', '').split(' ')[1]

        return Token.objects.get(key=token).user.organization

    @cached_property
    def get_business_unit(self):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.organization.business_unit

        token = request.headers.get('authorization', '').split(' ')[1]

        return Token.objects.get(key=token).user.organization.business_unit

    def create(self, validated_data):
        validated_data['organization'] = self.get_organization
        validated_data['business_unit'] = self.get_business_unit
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['organization'] = self.get_organization
        validated_data['business_unit'] = self.get_business_unit
        return super().update(instance, validated_data)
