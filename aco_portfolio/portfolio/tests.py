from django.test import TestCase
import networkx as nx
from networkx.readwrite import json_graph
import json
import unittest
from portfolio.models import Portfolio, Drug
# Create your tests here.
from solution.classes.graph_wrapper import GraphWrapper
from django.core.urlresolvers import reverse


class GraphWrapperTest(unittest.TestCase):

	
	def setUp(self):
		port = Portfolio.objects.get(pk=1)
		self.drug_qset = port.drug_set.all()
		self.wrapper = self.create_wrapper()
		self.drugs = self.wrapper.get_drugs()


	def create_wrapper(self):
		return GraphWrapper(self.drug_qset)
	#---------------------------------------------#

	def test_wrapper_creation(self):
		g = self.wrapper
		self.assertTrue(isinstance(g,GraphWrapper))

		self.assertNotEqual(g,None)
		self.assertEqual(g.drugs, self.drugs)

		self.assertNotEqual(g.food, None)
		self.assertNotEqual(g.nest, None)

	def test_get_wrapper_graph(self):
		g = self.wrapper.get_graph()

		self.assertTrue(isinstance(g, nx.Graph))

		# minus 2 for the 'food' and 'nest' nodes
		count = len(g.nodes())-2
		self.assertEqual(count, len(self.drugs))
		self.assertNotEqual(g,None)

	def test_get_serialized_wrapper_graph(self):
		g = self.wrapper.get_serialized_graph()

		self.assertNotEqual(g, None)
		self.assertNotEqual(g, "")
		
		count = len(json.loads(g)['nodes'])
		self.assertEqual(count, len(self.drugs)+2)