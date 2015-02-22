from django.shortcuts import render
from models import Portfolio, Drug
from django.http import HttpResponse,HttpResponseBadRequest
import json
from django.core import serializers


# Create your views here.
def home(request):
    context = {}

    portfolio = Portfolio.objects.get(pk=1)
    drugs = portfolio.drug_set.all()

    context["portfolio"] = portfolio
    context["drugs"] = drugs

    return render(request, 'home.html', context)


def d3(request):
	return render(request, 'd3.html')

	
def add_drug(request):
	pass

def delete_drug(request):
	pass

def update_drug(request):
	pass

def portfolio_data(request):
	portfolio = Portfolio.objects.get(pk=1)
	drugs = portfolio.drug_set.all()

	context = get_home_data(portfolio, drugs)


	return HttpResponse(context, content_type='application/json')

def get_home_data(portfolio, drugs):

	result = { 'portfolio': {
					'name': "",
					'budget': "",
					'drugs': {},
					'duration': ""
		}	
	}

	result['portfolio']['name'] = portfolio.name
	result['portfolio']['budget'] = portfolio.budget
	result['portfolio']['duration'] = portfolio.duration

	for drug in drugs: 
		d = {'profit_year' : drug.profit_year, 'stages': {}}
		for stage in drug.stage_set.all():
			s = {'fail' : stage.fail, 'cost': stage.cost, 'duration' : stage.duration}
			d['stages'][stage.name] = s

		result['portfolio']['drugs'][drug.name] = d


	return json.dumps(result)