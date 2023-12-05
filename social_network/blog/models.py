from django.contrib.auth.models import AbstractUser
from djongo import models
from djongo.models import DjongoManager
from django.utils.timezone import now
import uuid

class CustomUser(AbstractUser):
    userId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    post_count = models.IntegerField(default=0)
    def __str__(self):
        return self.username
 

class FriendShipRelations(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    requestId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    senderId = models.UUIDField()
    sender_username = models.CharField(max_length=50)
    receiverId = models.UUIDField()
    receiver_username = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)


class Post(models.Model):
    postId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=5000)
    created_date = models.DateTimeField(default=now, editable=False)
    views = models.IntegerField(default=0)
    authors = models.CharField(max_length=100, blank=False)
    objects = DjongoManager()

    def __str__(self):
         return self.title


class Comment(models.Model):
    commentId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    commented_post = models.UUIDField()
    commented_by = models.CharField(max_length=100)
    content = models.TextField(max_length=3000)


class Like(models.Model):
    likeId = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, primary_key=True)
    liked_objId = models.UUIDField()
    who_likedId = models.UUIDField()
