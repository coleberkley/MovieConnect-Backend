from django.contrib.auth.models import AbstractUser
from django.db import models

class GenericUser(AbstractUser):
    # AbstractUser automatically includes username, email, and password fields
    # Primary key is not username, but an internal id
    bio = models.TextField(null=True, blank=True)

