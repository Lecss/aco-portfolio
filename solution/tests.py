from django.test import TestCase
import networkx as nx
from networkx.readwrite import json_graph
import json
import unittest
from portfolio.models import Portfolio, Drug
from classes.portfolio import PortfolioCtrl
# Create your tests here.
from classes.graph_wrapper import GraphWrapper
from classes.ant import Ant
from classes.min_max2 import MinMax
from classes.expected_value import ExpectedValue
from django.core.urlresolvers import reverse
from classes.portfolio import PortfolioCtrl

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
                stage_curr_keys = ["cost","duration","succeed_prob", "drug", "active"]
                self.assertTrue( stage_curr_keys <= stage_val.keys())
                self.assertEquals(len(stage_val), len(stage_curr_keys))
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

#min-max 2
class MinMaxTest(unittest.TestCase):
    def setUp(self):
        port = Portfolio.objects.get(pk=1)
        port_ctrl = PortfolioCtrl(port)
        drug_qset = port.drug_set.all()
        wrapper = GraphWrapper(drug_qset)
        self.graph = wrapper.get_graph()
        self.mx = MinMax(wrapper, port_ctrl)

    def test_initialize_ants(self):
        self.assertTrue(len(self.mx.ants)== 0)
        self.mx.initialize_ants(100)
        self.assertTrue(len(self.mx.ants)== 100)
        #TBC

    def test_get_drug_ratio(self):
        #set_drugs()
        drug_A = self.graph.node["A1"]["drug"]
        ratio = self.mx.get_drug_ratio(drug_A)

        self.assertEquals(ratio, 0.252 * (10000 - 7000) * 1/8)

    def test_next_best_drugs_by_ratio(self):
        path = ["A1", "A2", "A3"]
        self.assertTrue(self.mx.next_best_drugs_by_ratio(path), ["D"])

    def test_get_alternatives_for_stage_fail(self):
        path = ["A1", "A2", "A3"]
        res = self.mx.get_alternatives_for_stage_fail(path, "A2")

        self.assertTrue(len(res) > 1)

   


    """def test_drug_expected_value(self):
                    self.set_drugs()
                       drugs = self.mx.wrapper.get_drugs()
            
                    self.mx.wrapper.profit_year["A"] = 10000
                    self.mx.wrapper.profit_year["C"] = 15000
            
            
                    self.assertEqual(self.mx.drug_expected_value("A",drugs["A"], 10), -1444)
                    self.assertEqual(int(self.mx.drug_expected_value("C",drugs["C"], 10)), 25520)"""


    """def test_path_expected_value(self):
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
            
                    self.assertEqual(totalAB_C, total-drugs["C"][2]["cost"])"""


    """def test_get_complete_drugs(self):
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
                    self.assertEquals(self.mx.get_complete_drugs(path4)['incomplete'], ["A1", "A2", "B2"])"""

class AntTest(unittest.TestCase):
    def setUp(self):
        port = Portfolio.objects.get(pk=1)
        self.drug_qset = port.drug_set.all()

        self.wrapper = GraphWrapper(self.drug_qset)
        self.drugs = self.wrapper.get_drugs()
        self.graph = self.wrapper.get_graph()
        
        self.ant_new = Ant(self.wrapper, port, [], [])
        self.ant_partial = Ant(self.wrapper, port, ["A1", "A2"], [])

    def test_move_next(self):
        ant = self.ant_new 
        self.assertEquals(ant.curr_node, "nest")
        ant.move_next("A1")
        self.assertEquals(ant.curr_node, "A1")
        self.assertTrue("A1" in ant.solution.path)

    def test_update_curr_node(self):
        ant = self.ant_new

        self.assertEquals(ant.curr_node, "nest")
        ant.update_curr_node("A1")
        self.assertTrue("nest" in ant.unavailable)
        self.assertTrue(ant.curr_node == "A1")

    def test_enable_next_node(self):
        ant = self.ant_new

        self.assertTrue("A2" in ant.not_active)
        ant.enable_next_node("A1")
        #print ant.not_active
        self.assertTrue("A2" not in ant.not_active)

    def test_update_partial_solution(self): 
        ant = self.ant_partial
        self.assertTrue(len(ant.solution.path) == 3)
        self.assertTrue("A2" in ant.solution.path)

    """ def test_update_capital(self):
                 self.ant.solution.path = ['nest', u'C2', u'C1', u'A3', u'A2', 'food']
                 self.ant.update_capital({"C":self.drugs["C"]}, 20, self.wrapper.profit_year)
                 print self.ant.generated
         
                 self.ant.solution.path = ['nest', u'C2', u'C1', u'A3', u'A2',u'A1', 'food']
                 self.ant.update_capital({"A":self.drugs["A"], "C":self.drugs["C"]}, 20, self.wrapper.profit_year)
                 print self.ant.generated"""

class ExpectedValueTest(unittest.TestCase):
    def setUp(self):
        self.port = Portfolio.objects.get(pk=1)
        self.drug_qset = self.port.drug_set.all()
        self.wrapper = GraphWrapper(self.drug_qset)
        self.drugs = self.wrapper.get_drugs()

        #print self.wrapper.get_graph().node["A3"]
        self.graph = self.wrapper.get_graph()

        self.path = ["A1", "A2", "A3", "C1", "C2"]
        port_ctrl = PortfolioCtrl(self.port)
        self.expected_value = ExpectedValue(self.graph, port_ctrl, self.path, [])

    def test_init_years(self):
        e = self.expected_value
        #print e.years
        self.assertTrue(len(e.years.keys()) != 0)
        self.assertTrue(len(e.years.keys()) == self.port.duration)


    def test_get_stage_complement(self):
        self.assertTrue(self.expected_value.get_stage_complement("A1") == ["A2", "A3"])

    def test_get_fixed_cost(self):
        self.expected_value.path = ["A1", "A2", "A3"]
        #print self.expected_value.get_fixed_cost() 
        self.assertTrue(self.expected_value.get_fixed_cost() == -7000)


#VIEWS









