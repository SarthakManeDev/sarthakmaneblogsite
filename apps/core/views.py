from django.http import HttpResponse
from django.shortcuts import render

from apps.blog.models import Post
from apps.reading.models import Book
from apps.tea.models import Exchange

from .models import AboutPhoto, Headline, MediaItem


def home(request):
    return render(request, "core/home.html", {
        "headlines": Headline.objects.filter(is_active=True)[:8],
        "books": Book.objects.filter(status=Book.READING),
        "recently_finished": Book.objects.filter(status=Book.FINISHED).order_by("-finished_on")[:3],
        "media": MediaItem.objects.filter(is_active=True)[:9],
        "latest_posts": Post.published.prefetch_related("subjects")[:3],
        "latest_tea": Exchange.objects.filter(is_published=True)[:2],
    })


def about(request):
    return render(request, "core/about.html", {"photos": AboutPhoto.objects.all()})


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")
