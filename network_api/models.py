from django.db import models
from django.contrib.auth.models import AbstractUser  
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    """Custom user model representing a user in the system."""

    def save(self, *args, **kwargs):
        """
        Saves the user object.
        This method sets the username field to the user's email address before saving the object.
        """
        self.username = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Returns a string representation of the user.
        Returns:
            str: The email address of the user.
        """
        return self.email
    

class FriendRequest(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_friend_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def accept(self):
        self.accepted = True
        self.save()

    def reject(self):
        self.delete()
