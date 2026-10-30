from django import template
from django.utils.safestring import mark_safe

from apps.core.markdown import render_markdown

register = template.Library()


@register.filter
def markdownify(text):
    return mark_safe(render_markdown(text))
