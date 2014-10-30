from django.shortcuts import render
from models import Portfolio, Drug


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
