from django.shortcuts import render
from classes.graph_wrapper import GraphWrapper
from classes.min_max2 import MinMax
from classes.portfolio import PortfolioCtrl
from portfolio.models import Portfolio, Drug, Stage
from django.http import HttpResponse,HttpResponseBadRequest
import json
import random



# Create your views here.
def get_solution(request):
	portfolio = Portfolio.objects.get(pk =1)
	#drugs = portfolio.drug_set.filter(name__in="EHICL" )

	drugs = portfolio.drug_set.all()

	"""
	vector = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","X","Y","Z","W"]

	portfolio2 = Portfolio(name="Leonard",budget=100000, duration =15, user=portfolio.user)
	portfolio2.save()

	for v in vector:
		d = Drug(name=v, portfolio = portfolio2, profit_year = random.randint(1000, 20000))
		d.save()

		for i in range(0,3):
			s = Stage(drug= d, name=i, fail = random.random(), cost=random.randint(1000, 10000), duration=random.randint(1,10))
			s.save()
	

	drugs = portfolio2.drug_set.all()"""

	graph_wrapper = GraphWrapper(drugs)	

	port_ctrl = PortfolioCtrl(portfolio)

	algo_session = MinMax(graph_wrapper, port_ctrl)
	#algo_session.run(300, 200)
	algo_session.run(40, 100)
	context = {}
	context['data'] = {}

	solutions = algo_session.best_solution_vector

	c = 0
	for sol in reversed(solutions):

		#print sol.ant.years
		if c > 4:
			continue
		entry = {}

		position_to_year = []
		for p in sol.path:
			for x in sol.ant.years:
				if p in sol.ant.years[x]["items"]:
					position_to_year.append(x)


		entry["generated"] = [sol.ant.years[x]["generated"] for x in sol.ant.years]
		entry["path"] = sol.path
		entry["per_year"] = position_to_year
		entry["years"] = sol.ant.years
		entry["budget_over_year"] = [sol.ant.years[x]["generated"] for x in sol.ant.years]
		entry["value"] = sol.value
		entry["running_time"] = sol.ant.time
		entry["graph"] = json.loads(graph_wrapper.get_serialized_graph())

		context['data'][c]=(entry)
		c+=1
	context['data']

	#print algo_session.in_
	#print algo_session.out_
	#print "================================================="
	return HttpResponse(json.dumps(context), content_type='application/json')

def get_graph(request):
	 
	portfolio = Portfolio.objects.get(pk = request.GET['portfolio_id'])
	drugs = portfolio.drug_set.all()
	graph_wrapper = GraphWrapper(drugs)
	
	context = graph_wrapper.get_serialized_graph()

	return HttpResponse(context, content_type='application/json')







