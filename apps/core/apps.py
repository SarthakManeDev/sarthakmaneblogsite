from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_delete, post_save

CONTENT_APPS = {"core", "blog", "tea", "reading", "auth"}


def _content_changed(sender, **kwargs):
    if sender._meta.app_label in CONTENT_APPS:
        from .backup import request_backup

        request_backup()


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        post_save.connect(_content_changed, dispatch_uid="backup_on_save")
        post_delete.connect(_content_changed, dispatch_uid="backup_on_delete")
        m2m_changed.connect(
            lambda sender, **kw: _content_changed(kw["model"]) if kw["action"].startswith("post_") else None,
            dispatch_uid="backup_on_m2m", weak=False,
        )
