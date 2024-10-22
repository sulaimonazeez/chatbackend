from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_friend")
    
    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"
    
    class Meta:
        unique_together = (("user", "friend"),)
        verbose_name = "Friendship"
        verbose_name_plural = "Friendships"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    class Meta:
        ordering = ['-timestamp']  # Latest messages appear first