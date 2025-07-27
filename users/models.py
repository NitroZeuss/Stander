from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
   username = models.CharField(max_length=150, unique=True)
   password = models.CharField(max_length=128)


   def __str__(self):
         return self.username

class ChatRoom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    persist_messages = models.BooleanField(default=False)


class Message(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."


   