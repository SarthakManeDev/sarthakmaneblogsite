from django.db import models


class Book(models.Model):
    READING, FINISHED, PAUSED, UP_NEXT = "reading", "finished", "paused", "up_next"
    STATUS_CHOICES = [
        (READING, "Reading"),
        (UP_NEXT, "Up next"),
        (PAUSED, "Paused"),
        (FINISHED, "Finished"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    cover = models.ImageField(upload_to="books/", blank=True)
    total_pages = models.PositiveIntegerField(default=1)
    current_page = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=READING)
    note = models.CharField(max_length=240, blank=True, help_text="A one-line thought, shown under the bar.")
    started_on = models.DateField(null=True, blank=True)
    finished_on = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    @property
    def percent(self):
        if self.status == self.FINISHED:
            return 100
        if not self.total_pages:
            return 0
        return min(100, round(self.current_page * 100 / self.total_pages))
