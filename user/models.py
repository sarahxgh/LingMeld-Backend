import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class user(AbstractUser): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    img = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    answers = models.JSONField(default=dict)
    evaluation = models.TextField(blank=True, default="") 
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save_answers(self, answers):
        """ Update the answers for the user. """
        if not self.answers:
            self.answers = []

    # Append the new answers
        if isinstance(self.answers, list):
            self.answers.extend(answers)  # Use `extend()` to append the list of answers
        else:
        # In case `answers` is not a list, handle it accordingly (e.g., converting it to a list)
            self.answers = [self.answers] + answers  # If it's a single object, convert it to a list

    # Save the updated answers to the database
        self.save()
    def save_evaluation(self, evaluation):
        self.evaluation = evaluation


    