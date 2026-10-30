from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Exchange


def exchange_list(request):
    exchanges = Exchange.objects.filter(is_published=True)
    page = Paginator(exchanges, 12).get_page(request.GET.get("page"))
    return render(request, "tea/list.html", {"page": page})


def exchange_detail(request, slug):
    qs = Exchange.objects if request.user.is_staff else Exchange.objects.filter(is_published=True)
    return render(request, "tea/detail.html", {"exchange": get_object_or_404(qs, slug=slug)})
