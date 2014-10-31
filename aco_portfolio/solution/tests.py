from django.test import TestCase
import networkx as nx
from networkx.readwrite import json_graph
import json
import unittest

# Create your tests here.
from classes.graph_wrapper import GraphWrapper
from django.core.urlresolvers import reverse


class GraphWrapperTest(unittest.TestCase):

	def setUp(self):
		self.drugs = ['A','B','C']
		self.wrapper = self.create_wrapper()

	def create_wrapper(self):
		return GraphWrapper(self.drugs)
	#---------------------------------------------#
	def test_wrapper_creation(self):
		g = self.wrapper
		self.assertTrue(isinstance(g,GraphWrapper))

		self.assertNotEqual(g,None)
		self.assertEqual(g.drugs, self.drugs)

		self.assertEqual(g.food, None)
		self.assertEqual(g.nest, None)

	def test_get_wrapper_graph(self):
		g = self.wrapper.get_graph()

		self.assertTrue(isinstance(g, nx.Graph))

		count = len(g.nodes())
		self.assertEqual(count, len(self.drugs))
		self.assertNotEqual(g,None)

	def test_get_serialized_wrapper_graph(self):
		g = self.wrapper.get_serialized_graph()

		self.assertNotEqual(g, None)
		self.assertNotEqual(g, "")

		count = len(json.loads(g)['nodes'])
		self.assertEqual(count, len(self.drugs))