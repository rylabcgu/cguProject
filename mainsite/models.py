from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	nickname = models.CharField(max_length=20, blank=True)
	gender = models.NullBooleanField()
	birthdate = models.DateField(null=True, blank=True)
	
	def __str__(self):
		return str(self.user)
