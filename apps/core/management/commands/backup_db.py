from django.core.management.base import BaseCommand

from apps.core.backup import backup_now, is_enabled


class Command(BaseCommand):
    help = "Back up the SQLite database to Azure Blob Storage."

    def handle(self, *args, **options):
        if not is_enabled():
            self.stdout.write("Backups need SQLite and Azure Storage settings; skipping.")
            return
        self.stdout.write(self.style.SUCCESS(f"Backed up to {backup_now()}"))
