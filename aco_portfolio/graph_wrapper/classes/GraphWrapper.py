import networkx as nx

class GraphWrapper():

	def __init__(self, drugs):
		self.food = None
		self.nest = None
		self.drugs = drugs
		self.graph = self.create_graph(drugs)


	def get_graph(self):
		return self.G

	def create_graph(self,drugs):
		self.G = nx.Graph()