from django.conf import settings
from django.db import models


# Create your models here.
class Link(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    url = models.URLField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="links",
        null=True,
        on_delete=models.CASCADE,
    )


class Vote(models.Model):
    link = models.ForeignKey(
        "links.Link", related_name="votes", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="votes", on_delete=models.CASCADE
    )
