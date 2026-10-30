from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Post
from apps.tea.models import Exchange


class StaticSitemap(Sitemap):
    def items(self):
        return ["core:home", "blog:list", "tea:list", "core:about"]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated_at


class ExchangeSitemap(Sitemap):
    def items(self):
        return Exchange.objects.filter(is_published=True)
