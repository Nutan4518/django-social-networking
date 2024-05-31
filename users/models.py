
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone

    
class Users(AbstractBaseUser):
    name            = models.CharField(max_length=25, null=False, blank=False, default=True)
    email           = models.EmailField(max_length=50, null=False, blank=False, unique=True)
    password        = models.CharField(max_length=1024, null=True, blank=True)
    is_active       = models.BooleanField(default=True)
    registered_on   = models.DateTimeField(auto_now_add=True)

    
    USERNAME_FIELD = 'email'

    

class Friends(models.Model):
    from_user = models.ForeignKey(Users, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Users, related_name='friendship_requests_received', on_delete=models.CASCADE)
    requested_at = models.DateTimeField(null=True, blank=True)
    accepted_at      = models.DateTimeField(null=True, blank=True)

    rejected_at = models.DateTimeField(null=True, blank=True)


    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    