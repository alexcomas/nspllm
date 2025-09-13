from django.utils.deprecation import MiddlewareMixin


class EnsureCORSHeadersMiddleware(MiddlewareMixin):
    """Fallback middleware to guarantee Access-Control-Allow-Origin when using older
    django-cors-headers versions or misconfiguration during local dev. Should NOT
    be used in production; prefer proper corsheaders configuration.
    """

    def process_response(self, request, response):
        origin = request.META.get("HTTP_ORIGIN")
        # If corsheaders already added header, leave it alone
        if "Access-Control-Allow-Origin" not in response:
            if origin:
                response["Access-Control-Allow-Origin"] = origin
            else:
                response["Access-Control-Allow-Origin"] = "*"
            # Minimal permissive headers for dev
            response.setdefault("Access-Control-Allow-Credentials", "true")
            response.setdefault(
                "Access-Control-Allow-Headers",
                "Authorization, Content-Type, Accept, X-Requested-With",
            )
            response.setdefault(
                "Access-Control-Allow-Methods",
                "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            )
        if request.method == "OPTIONS":
            response.status_code = 200
        return response
