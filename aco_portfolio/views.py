from django.shortcuts import render
from algo_core.classes.MinMax import MinMax
from models import Portfolio, Drug
from graph_wrapper.classes.GraphWrapper import GraphWrapper

# Create your views here.
def home(request):
	 portfolio = Portfolio.objects.all()
	 drugs = Drug.objects.all()
	 
	 context["portfolio"] = portfolio
	 context["drugs"] = drugs
	 return render(request, 'home.html', context)


