"""Fill an empty local database with sample content to see the design."""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.blog.models import Post
from apps.core.models import Headline, SiteProfile
from apps.reading.models import Book
from apps.studio.forms import PostForm
from apps.tea.models import Exchange

LOREM = (
    "Some ideas only make sense once you have walked around them a few times. "
    "This is a note about noticing, slowing down, and writing things down before they disappear. "
) * 30


class Command(BaseCommand):
    help = "Create sample content for local development."

    def handle(self, *args, **options):
        profile = SiteProfile.load()
        profile.tagline = profile.tagline or "Reading, writing, and asking questions."
        profile.bio = profile.bio or "Hi, I'm Sarthak. This is my corner of the internet."
        profile.save()

        today = date.today()
        for i, text in enumerate([
            "Started learning to make pour-over coffee properly.",
            "Booked a trip to the mountains for December.",
            "Finished my first 10k run.",
        ]):
            Headline.objects.get_or_create(text=text, defaults={"date": today - timedelta(days=i * 4)})

        Book.objects.get_or_create(title="The Overstory", defaults={
            "author": "Richard Powers", "total_pages": 502, "current_page": 214, "note": "Trees are patient narrators."})
        Book.objects.get_or_create(title="Meditations", defaults={
            "author": "Marcus Aurelius", "total_pages": 254, "current_page": 60})

        samples = [
            ("On slow mornings", "en", "life, habits", 1),
            ("Why I keep a reading log", "en", "books", 3),
            ("Notes from a long walk", "en", "travel, life", 8),
        ]
        for title, lang, subjects, repeat in samples:
            if Post.objects.filter(title=title).exists():
                continue
            form = PostForm(data={
                "title": title, "excerpt": "A short reflection.", "body": "## A beginning\n\n" + LOREM * repeat,
                "language": lang, "subjects_text": subjects, "status": Post.PUBLISHED,
            })
            form.is_valid() and form.save()

        Exchange.objects.get_or_create(question="Why does tea taste different in a clay cup?", defaults={
            "ai_name": "Claude", "asked_on": today,
            "answer": "Unglazed clay is porous. It absorbs a little of the liquid and its aroma... " + LOREM})
        self.stdout.write(self.style.SUCCESS("Demo content ready."))
