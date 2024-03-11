import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class RocketLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        duration = (now() - request._logging_start_time).total_seconds()  # noqa: SLF001
        handler = (
            request.resolver_match.url_name if request.resolver_match else 'UNKNOWN'
        )
        client = (
            f"{request.META.get('REMOTE_ADDR', '')}:"
            f"{request.META.get('REMOTE_PORT', 'UNKNOWN')}"
        )

        logger = logging.getLogger('django')
        logger.info(
            'HTTP Request',
            extra={
                'method': request.method,
                'path': request.get_full_path(),
                'status': response.status_code,
                'handler': handler,
                'time_taken': duration,
                'client': client,
                'size': len(response.content),
            },
        )

        return response

    def process_request(self, request):
        request._logging_start_time = now()  # noqa: SLF001
