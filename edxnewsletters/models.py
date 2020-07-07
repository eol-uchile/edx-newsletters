
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class EdxNewslettersUnsuscribed(models.Model):
    user_email = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False)