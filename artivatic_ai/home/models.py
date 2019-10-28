from django.db import models
from artivatic_ai.common.models import BaseModel

# Create your models here.
class UserEmail(BaseModel):
    """docstring for UserEmail"""

    email = models.CharField(max_length=200)

    def __str__(self):
        return self.email