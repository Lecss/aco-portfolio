from aco import ACO
from graph_wrapper import GraphWrapper

class MinMax(ACO):
	def __init__(self, graph):
		self.G = graph

	def run(self):
		return self.G
	
	def initialize_ants(self,ants_no):
		pass

	def initialize_pheromones(self, value=0.1):
		pass