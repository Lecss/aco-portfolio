import networkx as nx 
import abc

class ACO():
	__metaclass__ = abc.ABCMeta

	def __init__(self):
		self.alpha = 1
		self.betha = 2
		self.G = None


	@abc.abstractmethod
	def initialize_pheromones(self):
		return

	@abc.abstractmethod
	def initialize_ants(self,number):
		return

	@abc.abstractmethod
	def run(self, iterations = 1000, ants_no = 100):
		return
