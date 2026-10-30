from django.conf import settings

from .models import SiteProfile


def site(request):
    return {
        "profile": SiteProfile.load(),
        "nav_items": [
            ("core:home", "Home"),
            ("blog:list", "Blogs"),
            ("tea:list", "Tea with AI"),
            ("core:about", "About"),
        ],
        "SITE_URL": settings.SITE_URL,
    }
