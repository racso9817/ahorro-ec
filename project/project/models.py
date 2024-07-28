from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)

class UserProfile(models.Model):
    phone_regex = RegexValidator(
        regex=r'^0\d{9}$',
        message="You must enter a valid phone number"
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    independent_worker = models.BooleanField(default=False)
    if independent_worker:
        iess = models.FloatField(default=17.6)
    else:
        iess = models.FloatField(default=9.45)
    phone = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    monthly_income = models.FloatField(blank=False, null=False)
    def __str__(self):
        return str(self.user.id) + '-' + self.user.username
    
class ExtraIncome(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False, null=False)
    description = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return str(self.user.id) + '-' + self.user.username
    
class Expenses(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False, null=False)
    description = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return str(self.user.id) + '-' + self.user.username