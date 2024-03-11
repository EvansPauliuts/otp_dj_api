from django.core.validators import RegexValidator


class PhoneValidator(RegexValidator):
    regex = r'^\+375(\s+)?\(?(17|29|33|44)\)?(\s+)?[0-9]{3}-?[0-9]{2}-?[0-9]{2}$'
    message = 'Phone number must be in the format: +375 (XX) XXX-XX-XX'


def business_unit_contract_upload_to(instance, filename):
    return f'business_units/{instance.entity_key}/{filename}'
