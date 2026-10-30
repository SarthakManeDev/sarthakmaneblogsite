from django.contrib import admin

from .models import Post, PostImage, Subject


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "language", "length", "published_at"]
    list_filter = ["status", "language", "length", "subjects"]
    search_fields = ["title", "body"]


admin.site.register([Subject, PostImage])
