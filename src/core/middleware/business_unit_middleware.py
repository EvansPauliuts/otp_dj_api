from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ValidationError

class BusinessUnitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if request.user.is_authenticated and not request.user.business_unit.paid:
                raise ValidationError(
                    'Your business unit is not paid, please contact your Account Manager',
                )

        except ValidationError as e:
            errors = e.messages
            return JsonResponse({'detail': errors[0]}, status=status.HTTP_403_FORBIDDEN)

        return self.get_response(request)
