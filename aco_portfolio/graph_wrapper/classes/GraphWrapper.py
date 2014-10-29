import networkx as nx
from networkx.readwrite import json_graph
import json

class GraphWrapper():

	def __init__(self, drugs):
		self.food = None
		self.nest = None
		self.drugs = drugs
		self.graph = self.create_graph(drugs)


	def get_graph(self):
		return self.G

	def get_serialized_graph(self):
		data = json_graph.node_link_data(self.G)
		return json.dumps(data)

	def create_graph(self,drugs):
		self.G = nx.Graph()