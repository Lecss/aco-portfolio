from ACO import ACO
from graph_wrapper.classes.GraphWrapper import GraphWrapper

class MinMax(ACO):
	def __init__(self, graph):
		self.G = graph


	def run(self):
		self.G.add_node(1)
		return self.G
	