import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class user(AbstractUser): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    img = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    