from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    """
    Event model that includes basic event details and schedule info.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, related_name='events', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class RSVP(models.Model):
    """
    RSVP links a user to an event with a response status.
    """
    RESPONSE_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('maybe', 'Maybe'),
    )
    user = models.ForeignKey(User, related_name='rsvps', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='rsvps', on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    responded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} RSVP: {self.response} for {self.event.title}"
