from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Exchange(models.Model):
    """A question asked to an AI and the answer it gave."""

    question = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    answer = models.TextField(help_text="Markdown allowed.")
    ai_name = models.CharField(max_length=60, blank=True, help_text="e.g. Claude, ChatGPT")
    asked_on = models.DateField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-asked_on", "-id"]

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.question)[:300] or "question"
            slug, n = base, 2
            while Exchange.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tea:detail", args=[self.slug])
