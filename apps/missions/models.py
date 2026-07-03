from django.db import models


class FavoriteMission(models.Model):
    mission_name = models.CharField(max_length=500)
    mission_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.mission_name
