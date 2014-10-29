from django.shortcuts import render
from algo_core.classes.MinMax import MinMax
from models import Company, Portfolio
from graph_wrapper.classes.GraphWrapper import GraphWrapper

# Create your views here.
def home(request):
	 return render(request, 'home.html')

def get_solution(request):
	drugs = request.POST['drug_list']

	graph_wrapper = GraphWrapper(drugs)

	algo_session = MinMax(graph_wrapper.get_graph())
	algo_session.run()
	context = {}
	context['graph'] = graph_wrapper.get_serialized_graph()

	return render(request, 'solution.html', context)

