from django.db import models

# Create your models here.

class Company(models.Model):
	name = models.CharField(max_length=100)

class Portfolio(models.Model):
	name = models.CharField(max_length=100)
	company = models.ForeignKey(Company)
	budget = models.DecimalField(decimal_places= 4, max_digits= 15)

class Drug(models.Model):
	name = models.CharField(max_length=100)
	portfolio = models.ForeignKey(Portfolio)

