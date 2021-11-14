from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"user {self.username}"

class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=500)
    time_date = models.DateTimeField()
    likes = models.PositiveIntegerField()
    owner = models.CharField(max_length=500, default="")
    liked_by = models.ManyToManyField(User, blank=True, related_name="liked_by_users")

    def __str__(self):
        return f"post {self.text}"

class UserFollowing(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(User, related_name="following_owner", on_delete=models.CASCADE)

    following = models.ManyToManyField(User, blank=True, related_name="following")

    def __str__(self):
        return f"{self.user_id}"

class UserFollower(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(User, related_name="followers_owner", on_delete=models.CASCADE)

    followers = models.ManyToManyField(User, blank=True, related_name="followers")

    def __str__(self):
        return f"{self.user_id}"