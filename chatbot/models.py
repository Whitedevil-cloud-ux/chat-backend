from django.db import models

class Conversation(models.Model):
    title = models.CharField(max_length=200, blank=True, default="")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="active")
    ai_summary = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.id} - {self.title or 'Untitled'}"
    
class Message(models.Model):
    SENDER_CHOICES = (("user", "user"), ("ai", "ai"))
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
