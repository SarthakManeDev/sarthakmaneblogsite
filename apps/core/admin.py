from django.contrib import admin

from .models import AboutPhoto, Headline, MediaItem, SiteProfile

admin.site.register([SiteProfile, AboutPhoto, Headline, MediaItem])
