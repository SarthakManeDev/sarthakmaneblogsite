from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from apps.blog.feeds import LatestPostsFeed
from apps.core.views import healthz

from .sitemaps import ExchangeSitemap, PostSitemap, StaticSitemap

admin.site.site_header = "sarthakmane.in"


def robots_txt(request):
    lines = [
        "User-agent: *",
        f"Disallow: /{settings.STUDIO_PATH}/",
        f"Disallow: /{settings.DJANGO_ADMIN_PATH}/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


urlpatterns = [
    path("", include("apps.core.urls")),
    path("blogs/", include("apps.blog.urls")),
    path("tea-with-ai/", include("apps.tea.urls")),
    path(f"{settings.STUDIO_PATH}/", include("apps.studio.urls")),
    path(f"{settings.DJANGO_ADMIN_PATH}/", admin.site.urls),
    path("feed/", LatestPostsFeed(), name="feed"),
    path("sitemap.xml", sitemap, {"sitemaps": {"static": StaticSitemap, "posts": PostSitemap, "tea": ExchangeSitemap}}),
    path("robots.txt", robots_txt),
    path("healthz", healthz),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
