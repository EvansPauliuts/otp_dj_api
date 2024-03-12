from typing import override

from core.utils.serializers import GenericModelSerializer
from rest_framework import serializers

from apps.accounts.api.serializers import MinimalUserSerializer
from apps.location.helpers import create_or_update_location_comments
from apps.location.helpers import create_or_update_location_contacts
from apps.location.models import Location
from apps.location.models import LocationCategory
from apps.location.models import LocationComment
from apps.location.models import LocationContact
from apps.location.models import States


class LocationCategorySerializer(GenericModelSerializer):
    class Meta:
        model = LocationCategory
        fields = '__all__'
        read_only_fields = ('organization', 'business_unit')
        extra_kwargs = {
            'organization': {'required': False},
            'business_unit': {'required': False},
        }


class LocationContactSerializer(GenericModelSerializer):
    class Meta:
        model = LocationContact
        fields = '__all__'
        read_only_fields = ('location', 'organization', 'business_unit')
        extra_kwargs = {
            'organization': {'required': False},
            'business_unit': {'required': False},
        }


class LocationCommentSerializer(GenericModelSerializer):
    comment_type_name = serializers.CharField(required=False, read_only=True)
    entered_by = MinimalUserSerializer(read_only=True, required=False)

    class Meta:
        model = LocationComment
        fields = '__all__'
        read_only_fields = (
            'location',
            'organization',
            'business_unit',
            'entered_by',
        )
        extra_kwargs = {
            'organization': {'required': False},
            'business_unit': {'required': False},
        }


class LocationSerializer(GenericModelSerializer):
    wait_time_avg = serializers.FloatField(required=False, read_only=True)
    pickup_count = serializers.IntegerField(required=False, read_only=True)
    location_comments = LocationCommentSerializer(many=True, required=False)
    location_contacts = LocationContactSerializer(many=True, required=False)
    location_colors = serializers.CharField(
        required=False,
        read_only=True,
        allow_blank=True,
    )
    location_category_name = serializers.CharField(
        required=False,
        read_only=True,
        allow_blank=True,
    )

    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ('organization', 'business_unit')
        extra_kwargs = {
            'organization': {'required': False},
            'business_unit': {'required': False},
        }

    def create(self, validated_data):
        organization = super().get_organization
        business_unit = super().get_business_unit

        user = self.context['request'].user

        location_comments_data = validated_data.pop('location_comments', [])
        location_contacts_data = validated_data.pop('location_contacts', [])

        validated_data['organization'] = organization
        validated_data['business_unit'] = business_unit
        location = Location.objects.create(**validated_data)

        create_or_update_location_comments(
            location=location,
            location_comments_data=location_comments_data,
            organization=organization,
            business_unit=business_unit,
            user=user,
        )
        create_or_update_location_contacts(
            location=location,
            location_contacts_data=location_contacts_data,
            organization=organization,
            business_unit=business_unit,
        )

        return location

    @override
    def update(self, instance, validated_data):
        organization = super().get_organization
        business_unit = super().get_business_unit

        user = self.context['request'].user

        location_comments_data = validated_data.pop('location_comments', [])
        location_contacts_data = validated_data.pop('location_contacts', [])

        if location_contacts_data:
            create_or_update_location_contacts(
                location=instance,
                business_unit=business_unit,
                organization=organization,
                location_contacts_data=location_contacts_data,
            )

        if location_comments_data:
            create_or_update_location_comments(
                location=instance,
                business_unit=business_unit,
                organization=organization,
                location_comments_data=location_comments_data,
                user=user,
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class StatesSerializer(GenericModelSerializer):
    class Meta:
        model = States
        fields = '__all__'
        read_only_fields = ('organization', 'business_unit')
        extra_kwargs = {
            'organization': {'required': False},
            'business_unit': {'required': False},
        }
