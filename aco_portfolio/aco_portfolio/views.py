from django.shortcuts import render
from algo_core.classes.MinMax import MinMax
from models import Portfolio, Drug
from graph_wrapper.classes.GraphWrapper import GraphWrapper

# Create your views here.
def home(request):
	 context = {}
	 """portfolio = Portfolio(user=request.user, name="Leopard", budget=15000)
	 	 	 	 portfolio.save()
	 	 	 
	 	 	 	 drug1= Drug(portfolio= portfolio, name = "A")
	 	 	 	 drug2= Drug(portfolio= portfolio, name = "B")
	 	 	 	 drug3= Drug(portfolio= portfolio, name = "C")
	 	 	 
	 	 	 	 drug1.save()
	 	 	 	 drug2.save()
	 	 	 	 drug3.save()"""

	 portfolio = Portfolio.objects.all()
	 drugs = Drug.objects.all()
	 
	 context["portfolio"] = portfolio
	 context["drugs"] = drugs
	 return render(request, 'home.html', context)

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

