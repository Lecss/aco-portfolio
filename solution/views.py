from django.shortcuts import render
from classes.graph_wrapper import GraphWrapper
from classes.min_max2 import MinMax
from classes.portfolio import PortfolioCtrl
from portfolio.models import Portfolio, Drug, Stage
from django.http import HttpResponse,HttpResponseBadRequest
import json
import random

from threading import Thread, current_thread
import threading
from time import sleep
import logging

import time

global_x = {}
ant_no =10
iters = 5
# Create your views here.
def get_solution(request):

	algo_session = get_algo_session(request)
	algo_session.run(iters, ant_no)
	context = {'data':{} }

	solutions = algo_session.best_solution_vector

	c = 0
	for sol in reversed(solutions):

		#print sol.ant.years
		if c > 4:
			continue
		entry = {}

		#entry["generated"] = [sol.ant.years[x]["generated"] for x in sol.ant.years]
		entry["path"] = sol.path
		entry["exp"] = algo_session.experience
		entry["value"] = sol.value
		entry["years"] = sol.years
		entry["running_time"] = sol.ant.time
		entry["graph"] = json.loads(algo_session.wrapper.get_serialized_graph())
		entry["budget_over_year"] = sol.budget_over_years
		entry["full_vector"] = sol.full_vector

		context['data'][c]=(entry)
		c+=1
	context["phs"] = algo_session.pheromones

	return HttpResponse(json.dumps(context), content_type='application/json')

def test():
	time_start = time.time()
	for i in range(100):
	#results_confidence(drugs, portfolio)
	  pass

	print "TOTAL TIME"
	print time.time() - time_start
	print global_x

def recalculate(request):
	#fail_index = int(request.GET.get("index"))
	failed = json.loads(request.GET.get("failed"))

	#print failed
	path = json.loads(request.GET.get("path"))

	fail_index = path.index(failed[-1])

	partial_sol = path[:int(fail_index)+1]
	algo_session = get_algo_session(request, partial_sol, failed)
	algo_session.run(iters, ant_no)
	context = {'data':{} }

	solutions = algo_session.best_solution_vector
	c = 0

	best_solution = solutions[0]

	for sol in solutions:
		if sol.value > best_solution.value:
			best_solution_value = sol

	
	sol = best_solution
		
	entry = {}

	#entry["generated"] = [sol.ant.years[x]["generated"] for x in sol.ant.years]
	entry["path"] = sol.path
	entry["exp"] = algo_session.experience
	entry["value"] = sol.value
	entry["years"] = sol.years
	entry["running_time"] = sol.ant.time
	entry["budget_over_year"] = sol.budget_over_years

	context['data'][c]=(entry)
	context["phs"] = algo_session.pheromones

	return HttpResponse(json.dumps(context),content_type="application/json")

def get_algo_session(request, partial_sol=[], failed=[]):
	portfolio = Portfolio.objects.get(pk =1)
	#drugs = portfolio.drug_set.filter(name__in="EHICL" )
	#drugs = portfolio.drug_set.filter(name__in="ABCDEFGIKL" )
	drugs = portfolio.drug_set.all()

	graph_wrapper = GraphWrapper(drugs)	
	port_ctrl = PortfolioCtrl(portfolio)
	algo_session = MinMax(graph_wrapper, port_ctrl, partial_sol, failed)

	return algo_session

def results_confidence(drugs, portfolio):

	graph_wrapper = GraphWrapper(drugs)	
	port_ctrl = PortfolioCtrl(portfolio)
	algo_session = MinMax(graph_wrapper, port_ctrl)
	algo_session.run(10, 50)
	solutions = algo_session.best_solution_vector
	best = 0
	for sol in solutions:
		if sol.value > best:
			best = sol.value

	if str(best) not in global_x.keys():
		global_x[str(best)] = 1
	else:
		global_x[str(best)] = global_x[str(best)] + 1


def get_graph(request):
	 
	portfolio = Portfolio.objects.get(pk = request.GET['portfolio_id'])
	drugs = portfolio.drug_set.all()
	graph_wrapper = GraphWrapper(drugs)
	
	context = graph_wrapper.get_serialized_graph()

	return HttpResponse(context, content_type='application/json')




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


