from django.shortcuts import render
from classes.graph_wrapper import GraphWrapper
from classes.min_max import MinMax
from classes.portfolio import PortfolioCtrl
from portfolio.models import Portfolio
from django.http import HttpResponse,HttpResponseBadRequest
import json

# Create your views here.
def get_solution(request):
	 
	portfolio = Portfolio.objects.get(pk = request.GET['portfolio_id'])
	drugs = portfolio.drug_set.all()
	graph_wrapper = GraphWrapper(drugs)

	port_ctrl = PortfolioCtrl(portfolio)

	print port_ctrl.model.budget

	algo_session = MinMax(graph_wrapper, port_ctrl)
	algo_session.run(100, 2000)
	
	context = algo_session.best_solution.path

	return HttpResponse(context, content_type='application/json')

def get_graph(request):
	 
	portfolio = Portfolio.objects.get(pk = request.GET['portfolio_id'])
	drugs = portfolio.drug_set.all()
	graph_wrapper = GraphWrapper(drugs)
	
	context = graph_wrapper.get_serialized_graph()

	return HttpResponse(context, content_type='application/json')