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
    market_category = models.CharField(max_length=100, blank=True, null=True)

    strengths = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    opportunities = models.TextField(blank=True, null=True)
    threats = models.TextField(blank=True, null=True)

    score_strengths = models.IntegerField(default=0)
    score_weaknesses = models.IntegerField(default=0)
    score_opportunities = models.IntegerField(default=0)
    score_threats = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    prd_content = models.TextField(blank=True, null=True)

    # Blockchain fields
    idea_hash = models.CharField(max_length=64, blank=True, null=True)
    blockchain_tx_hash = models.CharField(max_length=100, blank=True, null=True)
    



class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests') 
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'idea')



    