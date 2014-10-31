from django.shortcuts import render
from classes.GraphWrapper import GraphWrapper
from classes.MinMax import MinMax

# Create your views here.
def get_solution(request):
	drugs = []
	drugs.append(request.POST['A'])
	drugs.append(request.POST['B'])
	drugs.append(request.POST['C'])
	
	graph_wrapper = GraphWrapper(drugs)

	algo_session = MinMax(graph_wrapper.get_graph())
	algo_session.run()
	
	context = {}
	context['graph'] = graph_wrapper.get_serialized_graph()

	return render(request, 'solution.html', context)