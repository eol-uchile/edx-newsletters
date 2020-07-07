
from django.db import models
# Create your models here.


class EdxNewslettersSuscribed(models.Model):
    suscribed = models.BooleanField(default=False)
    email = models.EmailField(
        max_length=255, unique=True, db_index=True)
