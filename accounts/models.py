from django.db import models

class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
         unique_together = ('investor', 'idea')