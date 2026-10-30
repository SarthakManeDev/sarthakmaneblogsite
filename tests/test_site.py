from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.blog.models import Post, Subject
from apps.reading.models import Book
from apps.tea.models import Exchange

# 1x1 transparent GIF
GIF = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"


def make_post(**kwargs):
    defaults = {"title": "Hello", "body": "word " * 100, "status": Post.PUBLISHED}
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


class PublicPagesTests(TestCase):
    def test_pages_render(self):
        make_post()
        Exchange.objects.create(question="Q?", answer="A", asked_on=timezone.now().date())
        for name in ["core:home", "blog:list", "tea:list", "core:about"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        for path in ["/robots.txt", "/sitemap.xml", "/feed/", "/healthz"]:
            self.assertEqual(self.client.get(path).status_code, 200, path)

    def test_drafts_and_scheduled_posts_are_hidden(self):
        draft = make_post(title="Draft", status=Post.DRAFT)
        future = make_post(title="Future", published_at=timezone.now() + timedelta(days=1))
        listing = self.client.get(reverse("blog:list")).content.decode()
        self.assertNotIn("Draft", listing)
        self.assertNotIn("Future", listing)
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(future.get_absolute_url()).status_code, 404)

    def test_blog_filters(self):
        topic = Subject.objects.create(name="Travel")
        a = make_post(title="Paris notes", language="fr")
        a.subjects.add(topic)
        make_post(title="Long read", body="word " * 4000)
        r = self.client.get(reverse("blog:list"), {"language": "fr"})
        self.assertContains(r, "Paris notes")
        self.assertNotContains(r, "Long read")
        r = self.client.get(reverse("blog:list"), {"length": Post.LONG})
        self.assertContains(r, "Long read")
        self.assertNotContains(r, "Paris notes")
        r = self.client.get(reverse("blog:list"), {"subject": "travel"})
        self.assertContains(r, "Paris notes")

    def test_markdown_is_sanitised(self):
        post = make_post(body="Hi <script>alert(1)</script> **bold**")
        html = self.client.get(post.get_absolute_url()).content.decode()
        self.assertIn("<strong>bold</strong>", html)
        self.assertNotIn("<script>alert", html)


class PostModelTests(TestCase):
    def test_slug_reading_time_and_length(self):
        a = make_post(title="Same title")
        b = make_post(title="Same title", body="word " * 2500)
        self.assertEqual(a.slug, "same-title")
        self.assertEqual(b.slug, "same-title-2")
        self.assertEqual(a.length, Post.SHORT)
        self.assertEqual(b.length, Post.MEDIUM)
        self.assertIsNotNone(a.published_at)


class StudioTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("sarthak", password="pw-long-enough-123", is_staff=True)

    def test_studio_requires_staff(self):
        url = reverse("studio:dashboard")
        self.assertRedirects(self.client.get(url), f"{reverse('studio:login')}?next={url}")
        get_user_model().objects.create_user("visitor", password="pw-long-enough-123")
        self.client.login(username="visitor", password="pw-long-enough-123")
        self.assertEqual(self.client.get(reverse("studio:post_list")).status_code, 403)

    def test_publish_blog_from_studio(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("studio:dashboard")).status_code, 200)
        r = self.client.post(reverse("studio:post_create"), {
            "title": "My first post", "body": "Hello **world**", "language": "en",
            "subjects_text": "Life, Books", "status": Post.PUBLISHED,
        })
        self.assertRedirects(r, reverse("studio:post_list"))
        post = Post.objects.get()
        self.assertEqual(sorted(post.subjects.values_list("name", flat=True)), ["Books", "Life"])
        self.assertContains(self.client.get(reverse("blog:list")), "My first post")

    def test_book_progress_updates_and_finishes(self):
        self.client.force_login(self.user)
        book = Book.objects.create(title="Dune", total_pages=400, current_page=10)
        self.client.post(reverse("studio:book_progress", args=[book.pk]), {"current_page": 200, "note": "Spice!"})
        book.refresh_from_db()
        self.assertEqual(book.percent, 50)
        self.assertContains(self.client.get(reverse("core:home")), "Spice!")
        self.client.post(reverse("studio:book_progress", args=[book.pk]), {"current_page": 400})
        book.refresh_from_db()
        self.assertEqual(book.status, Book.FINISHED)
        self.assertIsNotNone(book.finished_on)

    @override_settings(MEDIA_ROOT="/tmp/sarthakmane-test-media")
    def test_editor_image_upload(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("studio:upload_image"), {"image": SimpleUploadedFile("a.gif", GIF, "image/gif")})
        self.assertEqual(r.status_code, 200)
        self.assertIn("/media/blog/images/", r.json()["url"])
        bad = self.client.post(reverse("studio:upload_image"), {"image": SimpleUploadedFile("a.txt", b"x", "text/plain")})
        self.assertEqual(bad.status_code, 400)

    def test_all_studio_pages_render(self):
        self.client.force_login(self.user)
        for prefix in ["post", "book", "headline", "media", "exchange", "photo"]:
            for suffix in ["list", "create"]:
                name = f"studio:{prefix}_{suffix}"
                self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("studio:profile")).status_code, 200)
