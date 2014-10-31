from django.shortcuts import render
from models import Portfolio, Drug

# Create your views here.
def home(request):
	 context = {}

	 portfolio = Portfolio.objects.get(pk=1)
	 drugs = portfolio.drug_set.all()
	 
	 context["portfolio"] = portfolio
	 context["drugs"] = drugs
	 return render(request, 'home.html', context)
