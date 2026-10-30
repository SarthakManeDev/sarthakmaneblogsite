from django.contrib.syndication.views import Feed

from apps.core.markdown import render_markdown

from .models import Post


class LatestPostsFeed(Feed):
    title = "Sarthak Mane — Blog"
    link = "/blogs/"
    description = "New writing from sarthakmane.in"

    def items(self):
        return Post.published.all()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or render_markdown(item.body)[:500]

    def item_pubdate(self, item):
        return item.published_at
