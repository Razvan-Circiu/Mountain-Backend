# myapp/models.py
from django.db import models

class Track(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    gpx_file = models.FileField(upload_to='gpx_files/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    track = models.ForeignKey(Track, related_name='reviews', on_delete=models.CASCADE)
    user = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.track.title} by {self.user}"
