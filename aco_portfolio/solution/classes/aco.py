import networkx as nx 
import abc
from solution import Solution
from ant import Ant

class ACO():
	__metaclass__ = abc.ABCMeta

	alpha = 3
	betha = 1
	p = 0.2

	def __init__(self):
		self.G = None
		self.ants = []
		


	@abc.abstractmethod
	def initialize_pheromones(self):
		return

	@abc.abstractmethod
	def initialize_ants(self,number):
		return

	@abc.abstractmethod
	def run(self, iterations = 1000, ants_no = 100):
		return
