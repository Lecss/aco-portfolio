from django.test import TestCase
import networkx as nx
from networkx.readwrite import json_graph
import json
import unittest
from portfolio.models import Portfolio, Drug
# Create your tests here.
from classes.graph_wrapper import GraphWrapper
from classes.ant import Ant
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
        #print g.nodes()
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


    def set_drugs(self):
    	self.mx.wrapper.drugs =  {"A": {1: {'duration': 2, 'fail': 0.6, 'cost': 1000.0, 'prob': 1},
				                       2: {'duration': 2, 'fail': 0.6, 'cost': 1000.0, 'prob': 0.6},
				                       3: {'duration': 4, 'fail': 0.7, 'cost': 5000.0, 'prob': 0.36}},

				                 "B": {1: {'duration': 2, 'fail': 0.2, 'cost': 3000.0, 'prob': 1},
				                       2: {'duration': 3, 'fail': 0.4, 'cost': 1000.0, 'prob': 0.2},
				                       3: {'duration': 1, 'fail': 0.5, 'cost': 2000.0, 'prob': 0.08}},

				                 "C": {1: {'duration': 1, 'fail': 0.8, 'cost': 4000.0, 'prob': 1},
				                       2: {'duration': 5, 'fail': 0.9, 'cost': 5000.0, 'prob': 0.8}}}


    def test_drug_expected_value(self):
    	self.set_drugs()
       	drugs = self.mx.wrapper.get_drugs()

        self.mx.wrapper.profit_year["A"] = 10000
        self.mx.wrapper.profit_year["C"] = 15000


        self.assertEqual(self.mx.drug_expected_value("A",drugs["A"], 10), -1444)
        self.assertEqual(int(self.mx.drug_expected_value("C",drugs["C"], 10)), 25520)


    def test_path_expected_value(self):
    	self.set_drugs()
    	drugs = self.mx.wrapper.get_drugs()

    	path = ['nest', u'A1', u'A2', u'B2', u'B1', u'A3', u'B3','food']
        path2 = ['nest', u'A1', u'A2', u'B2', u'B1', u'A3', u'B3',"C2",'food']

        path_no_food = ['nest', u'A1', u'A2', u'B2', u'B1', u'A3', u'B3']

        self.mx.wrapper.profit_year["A"] = 10000
        self.mx.wrapper.profit_year["B"] = 20000
        self.mx.wrapper.profit_year["C"] = 15000
        #-------------------------------------------------------------------#
        
        total = self.mx.drug_expected_value("A",drugs["A"], 10) + self.mx.drug_expected_value("B",drugs["B"], 10)
        totalAB= self.mx.path_expected_value(path,10)

        totalABnf= self.mx.path_expected_value(path_no_food,10)

        totalAB_C= self.mx.path_expected_value(path2 ,10)

        self.assertEqual(total, totalAB)
        self.assertEqual(total, totalABnf)

        self.assertEqual(totalAB_C, total-drugs["C"][2]["cost"])


    def test_get_complete_drugs(self):
    	path = ['nest', u'A1', u'A2', u'B2', u'B1', u'A3', u'B3','food']
        path_no_food = ['nest', u'A1', u'A2', u'B2', u'B1', u'A3', u'B3']
        path2 = ['nest', u'A1', u'A2', u'B2', u'B1', u'A3', u'B3',u'C2','food']
        path3 = ['nest']
        path4 = ['nest', u'A1', u'A2', u'B2'] 

        self.assertEquals(len(self.mx.get_complete_drugs(path)['complete']), 2)
        self.assertEquals(len(self.mx.get_complete_drugs(path_no_food)['complete']), 2)
        self.assertEquals(len(self.mx.get_complete_drugs(path2)['complete']), 2)
        self.assertEquals(len(self.mx.get_complete_drugs(path3)['complete']), 0)

        self.assertEquals(len(self.mx.get_complete_drugs(path2)['incomplete']), 1)
        self.assertEquals(self.mx.get_complete_drugs(path2)['incomplete'], ["C2"])
        self.assertEquals(self.mx.get_complete_drugs(path4)['incomplete'], ["A1", "A2", "B2"])


class AntTest(unittest.TestCase):
    def setUp(self):
        port = Portfolio.objects.get(pk=1)
        self.drug_qset = port.drug_set.all()
        self.wrapper = GraphWrapper(self.drug_qset)
        self.drugs = self.wrapper.get_drugs()
        self.graph = self.wrapper.get_graph()
        
        self.ant = Ant(self.wrapper.nest, self.wrapper.food, self.graph)


    def test_update_capital(self):
    	self.ant.solution.path = ['nest', u'C2', u'C1', u'A3', u'A2', 'food']
    	self.ant.update_capital({"C":self.drugs["C"]}, 20, self.wrapper.profit_year)
    	print self.ant.generated

    	self.ant.solution.path = ['nest', u'C2', u'C1', u'A3', u'A2',u'A1', 'food']
    	self.ant.update_capital({"A":self.drugs["A"], "C":self.drugs["C"]}, 20, self.wrapper.profit_year)
    	print self.ant.generated





















