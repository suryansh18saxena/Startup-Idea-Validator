from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Ideas(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem_statement = models.TextField()
    solution  = models.TextField()
    market = models.TextField()
    unique_value = models.TextField()
    revenue_model = models.TextField()
    known_competitors = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
