import math
import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

WORDS_PER_MINUTE = 220


class Subject(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.PUBLISHED, published_at__lte=timezone.now())


class Post(models.Model):
    DRAFT, PUBLISHED = "draft", "published"
    STATUS_CHOICES = [(DRAFT, "Draft"), (PUBLISHED, "Published")]

    SHORT, MEDIUM, LONG = "short", "medium", "long"
    LENGTH_CHOICES = [(SHORT, "Short (< 5 min)"), (MEDIUM, "Medium (5–15 min)"), (LONG, "Long (15+ min)")]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("mr", "Marathi"),
        ("fr", "French"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True, help_text="One or two lines shown on the card.")
    body = models.TextField(help_text="Markdown. Use the image button to insert photos.")
    cover = models.ImageField(upload_to="blog/covers/", blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="en")
    subjects = models.ManyToManyField(Subject, blank=True, related_name="posts")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    reading_minutes = models.PositiveIntegerField(default=1, editable=False)
    length = models.CharField(max_length=10, choices=LENGTH_CHOICES, default=SHORT, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["status", "published_at"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "post"
            slug, n = base, 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        words = len(re.findall(r"\w+", self.body or ""))
        self.reading_minutes = max(1, math.ceil(words / WORDS_PER_MINUTE))
        if self.reading_minutes < 5:
            self.length = self.SHORT
        elif self.reading_minutes < 15:
            self.length = self.MEDIUM
        else:
            self.length = self.LONG
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", args=[self.slug])

    @property
    def is_live(self):
        return self.status == self.PUBLISHED and self.published_at and self.published_at <= timezone.now()


class PostImage(models.Model):
    """Images uploaded from the editor and referenced inside a post body."""

    image = models.ImageField(upload_to="blog/images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name
