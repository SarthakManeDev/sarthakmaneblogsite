"""Markdown rendering shared by blogs and Tea with AI answers.

Content is written by the site owner, but it is still sanitised so a pasted
snippet can never inject scripts into the public site.
"""
import markdown as md
import nh3

ALLOWED_TAGS = {
    "a", "abbr", "b", "blockquote", "br", "code", "del", "em", "figcaption", "figure",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "li", "ol", "p", "pre",
    "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
    "video", "source",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "loading"},
    "video": {"src", "controls", "poster", "preload"},
    "source": {"src", "type"},
    "code": {"class"},
    "span": {"class"},
    "th": {"align"},
    "td": {"align"},
}


def render_markdown(text: str) -> str:
    html = md.markdown(text or "", extensions=["extra", "sane_lists", "smarty"])
    html = html.replace("<img ", '<img loading="lazy" ')
    return nh3.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, link_rel="noopener noreferrer")
