from django.db import models

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} in {self.room_name} at {self.timestamp}"
