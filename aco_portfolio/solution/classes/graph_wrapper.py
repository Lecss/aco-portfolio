import networkx as nx
from networkx.readwrite import json_graph
import json


class GraphWrapper():
    def __init__(self, drug_qset):
        self.food = "food"
        self.nest = "nest"
        self.drugs = self.extract_drugs_from_qset(drug_qset)
        self.G = self.create_graph()
        self.compute_drug_probabilities()
        self.profit_year = self.compute_profit(drug_qset)

    def compute_profit(self,drug_qset):
        profit = {}

        for drug in drug_qset:
            profit[drug.name] = drug.profit_year

        return profit


    def extract_drugs_from_qset(self, drug_qset):
        result = {}
        for drug in drug_qset:
            result[drug.name] = {}
            count = 1
            for stage in drug.stage_set.all():
                stage_info = {}
                stage_info["cost"] = stage.cost
                stage_info["duration"] = stage.duration
                stage_info["fail"] = stage.fail

                result[drug.name][count] = stage_info
                count += 1

        # test no 'nodes' in the result is what expected : = no of all incoming stages
        return result

    def get_graph(self):
        return self.G

    def get_serialized_graph(self):
        data = json_graph.node_link_data(self.G)
        return json.dumps(data)

    def create_graph(self):
        g = nx.Graph()

        self.add_nodes(g)
        self.add_edges(g)
        return g

    def add_nodes(self, g):
        for drug in self.drugs:
            for key, val in self.drugs[drug].iteritems():
                g.add_node(drug + str(key), cost=val["cost"], duration=val["duration"])

        g.add_node(self.food, cost=0, duration=0)
        g.add_node(self.nest, cost=0, duration=0)

    def add_edges(self, g):
        for n in g.nodes():
            for y in g.nodes():
                if n is not y:
                    g.add_edge(n, y)


    def get_drugs(self):
        return self.drugs

    def compute_drug_probabilities(self):

        for drug in self.drugs:
            prev_stage_val = None

            for x in range(1, len(self.drugs[drug]) + 1):
                if x is 1:
                    self.drugs[drug][x]["prob"] = 1
                else:
                    self.drugs[drug][x]["prob"] = prev_stage_val["prob"] * prev_stage_val["fail"]

                prev_stage_val = self.drugs[drug][x]











