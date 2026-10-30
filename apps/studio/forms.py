from django import forms
from django.utils.text import slugify

from apps.blog.models import Post, Subject
from apps.core.models import AboutPhoto, Headline, MediaItem, SiteProfile
from apps.reading.models import Book
from apps.tea.models import Exchange

DATE = forms.DateInput(attrs={"type": "date"})


class PostForm(forms.ModelForm):
    subjects_text = forms.CharField(
        label="Subjects",
        required=False,
        help_text="Comma separated, e.g. philosophy, travel. New subjects are created automatically.",
    )

    class Meta:
        model = Post
        fields = ["title", "excerpt", "cover", "body", "language", "subjects_text", "status", "published_at"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 24, "data-editor": "markdown"}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }
        help_texts = {"published_at": "Leave empty to publish now. A future date schedules the post."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["subjects_text"].initial = ", ".join(s.name for s in self.instance.subjects.all())

    def save(self, commit=True):
        post = super().save(commit=commit)
        names = [n.strip() for n in self.cleaned_data["subjects_text"].split(",") if n.strip()]
        subjects = []
        for name in names:
            subject = Subject.objects.filter(slug=slugify(name)).first() or Subject.objects.create(name=name)
            subjects.append(subject)
        post.subjects.set(subjects)
        return post


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "cover", "total_pages", "current_page", "status", "note", "started_on", "finished_on"]
        widgets = {"started_on": DATE, "finished_on": DATE}


class BookProgressForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["current_page", "note"]


class HeadlineForm(forms.ModelForm):
    class Meta:
        model = Headline
        fields = ["text", "link", "date", "is_active"]
        widgets = {"date": DATE}


class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ["kind", "file", "embed_url", "caption", "date", "is_active"]
        widgets = {"date": DATE}


class ExchangeForm(forms.ModelForm):
    class Meta:
        model = Exchange
        fields = ["question", "answer", "ai_name", "asked_on", "is_published"]
        widgets = {"asked_on": DATE, "answer": forms.Textarea(attrs={"rows": 18})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = SiteProfile
        fields = ["name", "tagline", "bio", "email", "phone", "instagram", "linkedin_url", "github_url", "x_url"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 6})}


class AboutPhotoForm(forms.ModelForm):
    class Meta:
        model = AboutPhoto
        fields = ["image", "caption", "order"]
