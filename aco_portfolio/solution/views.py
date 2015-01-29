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
	#drugs = portfolio.drug_set.filter(name__in="CILGADH" )

	drugs = portfolio.drug_set.all()
	
	graph_wrapper = GraphWrapper(drugs)

	port_ctrl = PortfolioCtrl(portfolio)

	algo_session = MinMax(graph_wrapper, port_ctrl)
	algo_session.run(200, 1000)
	context = {}
	context['data'] = {}



	solutions = algo_session.solutions_found

	c = 0
	for sol in reversed(solutions):

		if c > 4:
			continue
		entry = {}
		entry["generated"] = sol.ant.generated
		entry["path"] = sol.path
		entry["per_year"] = sol.ant.position_to_year
		entry["budget_over_year"] = sol.ant.merged_glob
		entry["value"] = sol.value
		entry["running_time"] = sol.ant.time

		context['data'][c]=(entry)
		c+=1

	return HttpResponse(json.dumps(context), content_type='application/json')

def get_graph(request):
	 
	portfolio = Portfolio.objects.get(pk = request.GET['portfolio_id'])
	drugs = portfolio.drug_set.all()
	graph_wrapper = GraphWrapper(drugs)
	
	context = graph_wrapper.get_serialized_graph()

	return HttpResponse(context, content_type='application/json')