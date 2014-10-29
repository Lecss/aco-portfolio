from django.shortcuts import render
from algo_core.classes.MinMax import MinMax
from models import Company, Portfolio

# Create your views here.
def home(request):
	 return render(request, 'home.html')

def get_solution(request):
	drugs = request.POST['drug_list']
	algo_session = MinMax(drugs)
	algo_session.run()

	return render(request, 'solution.html')

