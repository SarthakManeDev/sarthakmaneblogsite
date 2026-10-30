from datetime import date

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.blog.models import Post, PostImage
from apps.core.models import AboutPhoto, Headline, MediaItem, SiteProfile
from apps.reading.models import Book
from apps.tea.models import Exchange

from . import forms


class StaffRequired(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


@staff_member_required(login_url=reverse_lazy("studio:login"))
def dashboard(request):
    cards = [
        {"title": "New blog", "text": "Write and publish a post.", "url": reverse("studio:post_create"), "primary": True},
        {"title": "Books", "text": f"{Book.objects.filter(status=Book.READING).count()} reading now. Update progress.", "url": reverse("studio:book_list")},
        {"title": "Blogs", "text": f"{Post.objects.count()} total, {Post.objects.filter(status=Post.DRAFT).count()} in draft.", "url": reverse("studio:post_list")},
        {"title": "Headlines", "text": "One-liners for the Home page.", "url": reverse("studio:headline_list")},
        {"title": "Photos & videos", "text": "Media for the Home page.", "url": reverse("studio:media_list")},
        {"title": "Tea with AI", "text": f"{Exchange.objects.count()} saved.", "url": reverse("studio:exchange_list")},
        {"title": "About", "text": "Bio, contact details and photos.", "url": reverse("studio:profile")},
    ]
    return render(request, "studio/dashboard.html", {"cards": cards})


# --- Generic CRUD -----------------------------------------------------------

def crud_views(model, form_class, prefix, label, columns, list_template="studio/object_list.html", initial=None,
               back_to=None, plural=None):
    """Build list/create/update/delete views for one model with shared templates."""
    list_url = reverse_lazy(back_to or f"studio:{prefix}_list")

    class Base(StaffRequired):
        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx.update(label=label, plural=plural or f"{label}s", prefix=prefix, columns=columns, list_url=list_url)
            return ctx

    class Saved:
        verb = "saved"

        def form_valid(self, form):
            messages.success(self.request, f"{label} {self.verb}.")
            return super().form_valid(form)

    class List(Base, ListView):
        template_name = list_template
        paginate_by = 50

    class Create(Base, Saved, CreateView):
        template_name = "studio/object_form.html"

        def get_initial(self):
            return initial() if initial else {}

    class Update(Base, Saved, UpdateView):
        template_name = "studio/object_form.html"
        verb = "updated"

    class Delete(Base, Saved, DeleteView):
        template_name = "studio/object_confirm_delete.html"
        verb = "deleted"

    for view in (List, Create, Update, Delete):
        view.model = model
        view.success_url = list_url
    Create.form_class = Update.form_class = form_class
    return List.as_view(), Create.as_view(), Update.as_view(), Delete.as_view()


today = lambda: {"date": date.today()}  # noqa: E731

post_views = crud_views(Post, forms.PostForm, "post", "Blog", ["title", "status", "published_at", "reading_minutes"],
                        list_template="studio/post_list.html")
book_views = crud_views(Book, forms.BookForm, "book", "Book", ["title", "status"],
                        list_template="studio/book_list.html", initial=lambda: {"started_on": date.today()})
headline_views = crud_views(Headline, forms.HeadlineForm, "headline", "Headline", ["text", "date", "is_active"], initial=today)
media_views = crud_views(MediaItem, forms.MediaItemForm, "media", "Media", ["caption", "kind", "date", "is_active"], initial=today,
                         plural="Photos & videos")
exchange_views = crud_views(Exchange, forms.ExchangeForm, "exchange", "Tea with AI", ["question", "ai_name", "asked_on", "is_published"],
                            initial=lambda: {"asked_on": date.today()}, plural="Tea with AI")
photo_views = crud_views(AboutPhoto, forms.AboutPhotoForm, "photo", "About photo", ["caption", "order"],
                         back_to="studio:profile")


# --- Special-purpose views --------------------------------------------------

@staff_member_required(login_url=reverse_lazy("studio:login"))
@require_POST
def book_progress(request, pk):
    """Quick update of the reading bar straight from the books list."""
    book = get_object_or_404(Book, pk=pk)
    form = forms.BookProgressForm(request.POST, instance=book)
    if form.is_valid():
        book = form.save(commit=False)
        book.current_page = min(book.current_page, book.total_pages)
        if book.current_page >= book.total_pages and book.status == Book.READING:
            book.status = Book.FINISHED
            book.finished_on = date.today()
            messages.success(request, f"Finished “{book.title}”. Nice!")
        else:
            messages.success(request, f"“{book.title}” is at {book.percent}%.")
        book.save()
    else:
        messages.error(request, "Could not update progress.")
    return redirect("studio:book_list")


@staff_member_required(login_url=reverse_lazy("studio:login"))
def profile(request):
    instance = SiteProfile.load()
    form = forms.ProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "About page updated.")
        return redirect("studio:profile")
    return render(request, "studio/profile.html", {"form": form, "photos": AboutPhoto.objects.all()})


@staff_member_required(login_url=reverse_lazy("studio:login"))
@require_POST
def upload_image(request):
    """Used by the blog editor's 'Insert image' button. Returns the image URL."""
    upload = request.FILES.get("image")
    if not upload or not (upload.content_type or "").startswith("image/"):
        return JsonResponse({"error": "Please choose an image file."}, status=400)
    image = PostImage.objects.create(image=upload)
    return JsonResponse({"url": image.image.url})
