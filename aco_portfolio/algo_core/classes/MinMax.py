from ACO import ACO
from graph_wrapper.classes.GraphWrapper import GraphWrapper

class MinMax(ACO):
	def __init__(self, drugs):
		wrapper = GraphWrapper(drugs)
		self.G = wrapper.get_graph()


	def run(self):
		return self.G
	