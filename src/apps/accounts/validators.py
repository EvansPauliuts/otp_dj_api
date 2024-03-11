from django.core.exceptions import ValidationError

def validate_org_timezone(value):
    import pytz

    try:
        pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError as e:
        raise ValidationError(
            '%(value)s is not a valid timezone',
            params={'value': value},
        ) from e
