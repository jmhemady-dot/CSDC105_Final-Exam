from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ROLE_CHOICES = (
        (2, 'Requestor'),
        (3, 'Approver'),
    )

    role_id = models.IntegerField(choices=ROLE_CHOICES, default=2)

    def __str__(self):
        return self.user.username


class Facility(models.Model):

    facility_id = models.AutoField(primary_key=True)
    facility_name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    capacity = models.IntegerField()

    def __str__(self):
        return self.facility_name

class Reservation(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    reservation_id = models.AutoField(primary_key=True)

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    purpose = models.TextField()
    attendees = models.IntegerField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.facility} - {self.requestor.username}"