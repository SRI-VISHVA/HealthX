from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Meal(models.Model):
    userfk = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
    quantity = models.FloatField()
    kcal = models.FloatField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"User {self.userfk}: meal {self.name} with {self.kcal, self.quantity} kcal, on {self.date}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal_cals = models.FloatField(blank=True, null=True, default='2000')
