from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups_users',  # Change related_name to be unique
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_users',  # Change related_name to be unique
        blank=True
    )
    phone = models.CharField(max_length=15, null=True, blank=True)


