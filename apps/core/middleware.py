from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Redirect alternate hosts (e.g. www.) to CANONICAL_HOST, if configured."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.host = settings.CANONICAL_HOST
        self.aliases = {f"www.{self.host}"} if self.host else set()

    def __call__(self, request):
        if self.aliases and request.get_host().split(":")[0] in self.aliases:
            return HttpResponsePermanentRedirect(f"https://{self.host}{request.get_full_path()}")
        return self.get_response(request)
