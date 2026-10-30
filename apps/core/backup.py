"""SQLite backups to Azure Blob Storage.

With SQLite there is no managed database doing backups for us, so every time
content changes we copy a consistent snapshot of the database to a private
blob container (throttled, in a background thread). A lifecycle rule on the
storage account deletes copies older than 30 days.
"""
import logging
import sqlite3
import tempfile
import threading
import time
from pathlib import Path

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

MIN_INTERVAL_SECONDS = 5 * 60
_lock = threading.Lock()
_last_started = 0.0
_pending = False


def is_enabled():
    db = settings.DATABASES["default"]
    return (
        db["ENGINE"] == "django.db.backends.sqlite3"
        and bool(settings.AZURE_ACCOUNT_NAME and settings.AZURE_ACCOUNT_KEY)
    )


def backup_now():
    """Snapshot the SQLite database and upload it. Returns the blob name."""
    from azure.storage.blob import BlobServiceClient

    source = sqlite3.connect(settings.DATABASES["default"]["NAME"])
    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / "db.sqlite3"
        target = sqlite3.connect(snapshot)
        try:
            source.backup(target)  # consistent copy even while the site is in use
        finally:
            target.close()
            source.close()
        name = timezone.now().strftime("db/%Y/%m/db-%Y%m%d-%H%M%S.sqlite3")
        client = BlobServiceClient(
            account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net",
            credential=settings.AZURE_ACCOUNT_KEY,
        )
        with snapshot.open("rb") as fh:
            client.get_blob_client(settings.BACKUP_CONTAINER, name).upload_blob(fh, overwrite=True)
    logger.info("Database backed up to %s/%s", settings.BACKUP_CONTAINER, name)
    return name


def _run(delay):
    global _pending
    time.sleep(delay)
    with _lock:
        _pending = False
    try:
        backup_now()
    except Exception:  # a failed backup must never break the site
        logger.exception("Database backup failed")


def request_backup():
    """Schedule a backup soon; bursts of saves collapse into one upload."""
    global _last_started, _pending
    if not is_enabled():
        return
    with _lock:
        if _pending:
            return
        _pending = True
        delay = max(0.0, _last_started + MIN_INTERVAL_SECONDS - time.monotonic())
        _last_started = time.monotonic() + delay
    threading.Thread(target=_run, args=(delay,), daemon=True).start()
