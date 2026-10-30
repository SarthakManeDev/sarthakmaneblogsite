import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from apps.core import backup


@override_settings(AZURE_ACCOUNT_NAME="acct", AZURE_ACCOUNT_KEY="key", BACKUP_CONTAINER="backups")
class BackupTests(SimpleTestCase):
    def test_backup_uploads_a_valid_sqlite_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "live.sqlite3"
            conn = sqlite3.connect(db_path)
            conn.execute("create table t (x)")
            conn.execute("insert into t values (42)")
            conn.commit()
            conn.close()

            uploaded = {}

            def fake_upload(fh, overwrite):
                uploaded["data"] = fh.read()

            db = {**settings.DATABASES["default"], "NAME": str(db_path)}
            with mock.patch.dict(settings.DATABASES, {"default": db}), \
                    mock.patch("azure.storage.blob.BlobServiceClient") as client_cls:
                blob = client_cls.return_value.get_blob_client.return_value
                blob.upload_blob.side_effect = fake_upload
                name = backup.backup_now()

            container, blob_name = client_cls.return_value.get_blob_client.call_args.args
            self.assertEqual(container, "backups")
            self.assertEqual(blob_name, name)
            self.assertTrue(name.startswith("db/") and name.endswith(".sqlite3"))
            self.assertTrue(uploaded["data"].startswith(b"SQLite format 3"))

    @override_settings(AZURE_ACCOUNT_NAME=None)
    def test_disabled_without_storage(self):
        self.assertFalse(backup.is_enabled())
        with mock.patch("threading.Thread") as thread:
            backup.request_backup()
        thread.assert_not_called()

    def test_bursts_of_saves_schedule_one_backup(self):
        backup._pending = False
        with mock.patch("threading.Thread") as thread:
            backup.request_backup()
            backup.request_backup()
            backup.request_backup()
        self.assertEqual(thread.call_count, 1)
        backup._pending = False
