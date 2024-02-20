from django.core.validators import RegexValidator


class PhoneValidator(RegexValidator):
    regex = r'^\+375(\s+)?\(?(17|29|33|44)\)?(\s+)?[0-9]{3}-?[0-9]{2}-?[0-9]{2}$'
    message = 'Exactly 12 digits are required'
