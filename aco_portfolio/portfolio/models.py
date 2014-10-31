from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Portfolio(models.Model):
	name = models.CharField(max_length=100)
	user = models.ForeignKey(User)
	budget = models.DecimalField(decimal_places= 4, max_digits= 15)

class Drug(models.Model):
	name = models.CharField(max_length=100)
	portfolio = models.ForeignKey(Portfolio)

class Stage(models.Model):
	name = models.CharField(max_length=10)
	drug = models.ForeignKey(Drug)
	shit = models.CharField(max_length=20)

