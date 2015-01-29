from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Portfolio(models.Model):
	name = models.CharField(max_length=100)
	user = models.ForeignKey(User)
	budget = models.FloatField(default=0)
	duration = models.IntegerField(default = 10)

class Drug(models.Model):
	name = models.CharField(max_length=100)
	portfolio = models.ForeignKey(Portfolio)
	profit_year = models.FloatField(default=0)

class Stage(models.Model):
	name = models.CharField(max_length=10)
	drug = models.ForeignKey(Drug)
	fail = models.FloatField(default=0.0)
	cost = models.FloatField(default=0)
	duration = models.IntegerField(default=0)

