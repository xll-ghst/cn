from django.conf import settings
from django.db import models

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lessons",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
