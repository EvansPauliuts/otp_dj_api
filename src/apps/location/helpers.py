from django.contrib.auth import get_user_model
from django.db import transaction

from apps.location.models import LocationComment
from apps.location.models import LocationContact

User = get_user_model()


@transaction.atomic
def create_or_update_location_comments(
    *,
    location,
    location_comments_data,
    organization,
    business_unit,
    user,
):
    created_comment = []

    if location_comments_data:
        existing_comment_id = set(
            location.location_comments.values_list('id', flat=True),
        )
        new_comment_id = set()

        for id_c in location_comments_data:
            id_c['business_unit'] = business_unit
            id_c['organization'] = organization

            contact, created = LocationComment.objects.update_or_create(
                id=id_c.get('id'),
                location=location,
                entered_by=user,
                defaults=location_comments_data,
            )
            created_comment.append(contact)

            if not created:
                new_comment_id.add(contact.id)

        to_delete_ids = existing_comment_id - new_comment_id
        LocationComment.objects.filter(id__in=to_delete_ids).delete()

    return created_comment


@transaction.atomic
def create_or_update_location_contacts(
    *,
    location,
    location_contacts_data,
    organization,
    business_unit,
):
    created_contracts = []

    if location_contacts_data:
        existing_contact_ids = set(
            location.location_contacts.values_list('id', flat=True),
        )
        new_contact_ids = set()

        for id_c in location_contacts_data:
            id_c['business_unit'] = business_unit
            id_c['organization'] = organization

            contact, created = LocationContact.objects.update_or_create(
                id=id_c.get('id'),
                location=location,
                defaults=location_contacts_data,
            )
            created_contracts.append(contact)

            if not created:
                new_contact_ids.add(contact.id)

        to_delete_ids = existing_contact_ids - new_contact_ids
        LocationContact.objects.filter(id__in=to_delete_ids).delete()

    return created_contracts
