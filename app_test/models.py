from uuid import uuid4
from django.db import models
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from django.db.models.base import ModelBase
from auditlog.registry import auditlog


#-----------------------meta class ----------------------------
class AuditLogModelBase(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        if not new_class._meta.abstract:
            auditlog.register(new_class)

        return new_class

class BaseModel(models.Model, metaclass=AuditLogModelBase):
    id = models.UUIDField(
        verbose_name=("unique id"),
        primary_key=True,
        unique=True,
        null=False,
        default=uuid4,
        editable=False
    )
    created_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name=("created by"),
    )
    created_at = models.DateTimeField(
        verbose_name=('created at'),
        default=timezone.now
    )

    class Meta:
        abstract = True
        indexes = (
            models.Index(fields=['id'], name='%(class)s_id_idx'),
        )

    class Meta:
        abstract = True
