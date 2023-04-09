from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Destination(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    popular = models.BooleanField(default=False)
    
class TripPlan(models.Model):
    destinations = models.ForeignKey(Destination, related_name="trip_plans", on_delete=models.CASCADE)

class User(AbstractUser):
    trip_plan = models.OneToOneField(TripPlan, related_name="booker", on_delete=models.CASCADE, blank=True, null=True)