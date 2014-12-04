from django.shortcuts import render
from classes.graph_wrapper import GraphWrapper
from classes.min_max import MinMax
from portfolio.models import Portfolio

# Create your views here.
def get_solution(request):
	 
	portfolio = Portfolio.objects.get(pk = request.POST['portfolio_id'])
	drugs = portfolio.drug_set.all()
	graph_wrapper = GraphWrapper(drugs)

	algo_session = MinMax(graph_wrapper)
	algo_session.run(1000, 100, portfolio.duration)
	
	context = {}
	context['graph'] = graph_wrapper.get_serialized_graph()
	return render(request, 'solution.html', context)