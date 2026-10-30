from django.core.exceptions import ValidationError
from django.db import models


class SiteProfile(models.Model):
    """Single row holding the About page and contact details."""

    name = models.CharField(max_length=120, default="Sarthak Mane")
    tagline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True, help_text="Short paragraph for the About page. Markdown allowed.")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    instagram = models.CharField(max_length=60, blank=True, help_text="Handle without @")
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True, verbose_name="X / Twitter URL")

    class Meta:
        verbose_name = "site profile"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutPhoto(models.Model):
    image = models.ImageField(upload_to="about/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or self.image.name


class Headline(models.Model):
    """One-liner about what's going on in life, shown on Home."""

    text = models.CharField(max_length=200)
    link = models.URLField(blank=True)
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.text


class MediaItem(models.Model):
    """A photo or video shown in the Home page feed."""

    PHOTO, VIDEO = "photo", "video"
    KIND_CHOICES = [(PHOTO, "Photo"), (VIDEO, "Video")]

    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=PHOTO)
    file = models.FileField(upload_to="home/", blank=True, help_text="Image or video file (mp4/webm).")
    embed_url = models.URLField(blank=True, help_text="Or a YouTube link instead of uploading a video.")
    caption = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.caption or f"{self.get_kind_display()} {self.date}"

    def clean(self):
        if not self.file and not self.embed_url:
            raise ValidationError("Upload a file or provide an embed URL.")

    @property
    def youtube_embed(self):
        """Turn a normal YouTube link into an embeddable one."""
        url = self.embed_url
        if "youtu.be/" in url:
            vid = url.rsplit("/", 1)[-1].split("?")[0]
        elif "watch?v=" in url:
            vid = url.split("watch?v=")[1].split("&")[0]
        elif "/embed/" in url:
            return url
        else:
            return ""
        return f"https://www.youtube-nocookie.com/embed/{vid}"
