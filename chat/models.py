from django.db import models
from django.contrib.auth.models import User
from dashboard.models import ScenarioModel, StudentModel

# Create your models here.
class ChatRoomModel(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name='chat_rooms')

class MessageModel(models.Model):
    room = models.ForeignKey(ChatRoomModel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.room.name}: {self.content}"

class ConversationHistory(models.Model):
    scenario = models.ForeignKey(ScenarioModel, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, null=True)
    messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['scenario', 'student']

    def __str__(self):
        return f"Historial de conversación para {self.student.user.username} en {self.scenario.name}"