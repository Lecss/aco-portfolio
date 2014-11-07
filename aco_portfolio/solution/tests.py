from django.test import TestCase
import networkx as nx
from networkx.readwrite import json_graph
import json
import unittest
from portfolio.models import Portfolio, Drug
# Create your tests here.
from classes.graph_wrapper import GraphWrapper
from classes.min_max import MinMax
from django.core.urlresolvers import reverse


class GraphWrapperTest(unittest.TestCase):

	
	def setUp(self):
		port = Portfolio.objects.get(pk=1)
		self.drug_qset = port.drug_set.all()
		self.wrapper = self.create_wrapper()
		self.drugs = self.wrapper.get_drugs()
		self.stages = 0
		for x,y in self.drugs.items():
			self.stages += len(y)


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
		print g.nodes()
		# minus 2 for the 'food' and 'nest' nodes
		count = len(g.nodes())-2

		self.assertEqual(count, self.stages)
		self.assertNotEqual(g,None)

	def test_get_serialized_wrapper_graph(self):
		g = self.wrapper.get_serialized_graph()

		self.assertNotEqual(g, None)
		self.assertNotEqual(g, "")
	
		count = len(json.loads(g)['nodes'])
		self.assertEqual(count, self.stages +2)

	def test_extract_drugs_from_qset(self):
		extracted = self.wrapper.extract_drugs_from_qset(self.drug_qset)

		self.assertTrue(extracted is not None)
		self.assertTrue(extracted is not [])
		self.assertEquals(len(self.drug_qset), len(extracted)) 

		for key, val in extracted.iteritems():
			for stage_key, stage_val in val.iteritems():
				stage_curr_keys = ["cost","duration","fail"]
				self.assertTrue( stage_curr_keys <= stage_val.keys())
				self.assertTrue(len(stage_val) == len(stage_curr_keys))
				self.assertTrue(isinstance(stage_key, int))

	def test_add_nodes(self):
		g = self.create_wrapper().get_graph()
		init_len = len(g.nodes())

		g.add_node("TEST_NODE")
		self.assertEquals(len(g.nodes()), init_len+1)
		self.assertTrue("TEST_NODE" in g.nodes())
		
	def test_create_graph(self):
		g = self.create_wrapper().get_graph()
		self.assertTrue(g is not None)
		self.assertTrue("food" in g.nodes())
		self.assertTrue("nest" in g.nodes())



class MinMaxTest(unittest.TestCase):
	def setUp(self):
		port = Portfolio.objects.get(pk=1)
		drug_qset = port.drug_set.all()
		wrapper = GraphWrapper(drug_qset)
		self.mx = MinMax(wrapper)
	

	def test_initialize_ants(self):
		self.assertTrue(len(self.mx.ants)== 0)
		self.mx.initialize_ants(100)
		self.assertTrue(len(self.mx.ants)== 100)
		#TBC


















