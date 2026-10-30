from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Post, Subject


def post_list(request):
    posts = Post.published.prefetch_related("subjects")
    filters = {
        "language": request.GET.get("language", ""),
        "subject": request.GET.get("subject", ""),
        "length": request.GET.get("length", ""),
        "q": request.GET.get("q", "").strip(),
    }
    if filters["language"]:
        posts = posts.filter(language=filters["language"])
    if filters["subject"]:
        posts = posts.filter(subjects__slug=filters["subject"])
    if filters["length"]:
        posts = posts.filter(length=filters["length"])
    if filters["q"]:
        posts = posts.filter(Q(title__icontains=filters["q"]) | Q(excerpt__icontains=filters["q"]) | Q(body__icontains=filters["q"]))

    page = Paginator(posts.distinct(), 12).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    used_languages = set(Post.published.values_list("language", flat=True))
    return render(request, "blog/list.html", {
        "page": page,
        "filters": filters,
        "querystring": query.urlencode(),
        "subjects": Subject.objects.filter(posts__status=Post.PUBLISHED).distinct(),
        "languages": [c for c in Post.LANGUAGE_CHOICES if c[0] in used_languages],
        "lengths": Post.LENGTH_CHOICES,
    })


def post_detail(request, slug):
    # Logged-in owner can preview drafts; everyone else only sees live posts.
    qs = Post.objects if request.user.is_staff else Post.published
    post = get_object_or_404(qs.prefetch_related("subjects"), slug=slug)
    return render(request, "blog/detail.html", {"post": post})
