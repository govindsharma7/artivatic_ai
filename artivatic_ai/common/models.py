import uuid
from django.db import models


# Create your models here.
class BaseModel(models.Model):
    """docstring for BaseModel"""
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Document(BaseModel):
    """docstring for Document"""

    file_name = models.CharField(max_length=120)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    file_url = models.CharField(max_length=200)

    def __str__(self):
        return self.file_name