import time
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse

# Dedicated logger name so we can configure formatting/level explicitly.
logger = logging.getLogger("api.request")

class RequestLoggingMiddleware:
    """Logs each incoming request when received and again when the response is returned.

    Format (start):  --> [METHOD] /path?query (client=IP)
    Format (end):    <-- [METHOD] /path?query status=X duration=YYYms size=ZZZB
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.time()
        path = request.get_full_path()
        method = request.method
        client_ip = request.META.get("REMOTE_ADDR", "-")
        logger.info(f"--> {method} {path} (client={client_ip})")
        try:
            response = self.get_response(request)
        except Exception:
            # Log exception separately; let Django default handlers proceed
            duration_ms = int((time.time() - start) * 1000)
            logger.exception(f"!!! {method} {path} raised exception after {duration_ms}ms")
            raise
        duration_ms = int((time.time() - start) * 1000)
        size = getattr(response, 'streaming_content', None)
        if size is None:
            content_length = len(response.content or b"") if hasattr(response, 'content') else 0
        else:
            # Can't easily measure streaming size without consuming iterator
            content_length = -1
        logger.info(
            f"<-- {method} {path} status={response.status_code} duration={duration_ms}ms size={content_length if content_length >= 0 else 'stream'}"
        )
        return response
