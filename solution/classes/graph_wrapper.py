import networkx as nx
from networkx.readwrite import json_graph
import json
from operator import mul

class GraphWrapper():
    def __init__(self, drug_qset):
        self.food = "food"
        self.nest = "nest"
        self.drug_qset = drug_qset
        self.drugs = self.extract_drugs_from_qset(drug_qset)
        self.drug_stages = self.map_stage_number(drug_qset)
        self.G = self.create_graph()
        self.compute_drug_probabilities()
        self.profit_year = self.compute_profit(drug_qset)

    def compute_profit(self,drug_qset):
        profit = {}

        for drug in drug_qset:
            profit[drug.name] = drug.profit_year

        return profit

    def map_stage_number(self, drug_qset):
        drug_stage_map = {}
        for drug in drug_qset:
            drug_stage_map[drug.name]= len(drug.stage_set.all())

        return drug_stage_map

    def extract_drugs_from_qset(self, drug_qset):
        result = {}
        for drug in drug_qset:
            result[drug.name] = {}
            count = 1
            for stage in drug.stage_set.all():
                stage_info = {}
                stage_info["cost"] = stage.cost
                stage_info["duration"] = stage.duration
                stage_info["succeed_prob"] = stage.fail
                stage_info["drug"] =  {"year_profit": drug.profit_year, "name": drug.name, "duration": sum(x for x in range(0,4))}

                if count is 1:
                    stage_info["active"] = True
                else:
                    stage_info["active"] = False
                
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
        for drug in self.drug_qset:
            for (i,stage) in enumerate(drug.stage_set.all()):
                g.add_node( drug.name + str(i+1),
                            index = i, 
                            cost= stage.cost, 
                            duration= stage.duration,
                            arrive_here_prob = 1 if i == 0 else g.node[drug.name + str(i)]["arrive_here_prob"] * g.node[drug.name + str(i)]["pass_prob"], 
                            active = (i == 0),
                            pass_prob = stage.fail,
                            start_stage= drug.name + str(1),
                            last_stage = drug.name + str(len(drug.stage_set.all())),
                            decision = {},
                            ph = 0,
                            drug = {
                                "name": drug.name,
                                "profit_per_year" : drug.profit_year,
                                "total_duration" : sum(x.duration for x in drug.stage_set.all()),
                                "stages_count" : len(drug.stage_set.all()),
                                "cummulated_prob" : reduce(mul, [x.fail for x in drug.stage_set.all()])
                            })
                

        g.add_node(self.food, cost=0, duration=0, active=True, index=1)
        g.add_node(self.nest, cost=0, duration=0, active = True, index=1)

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
                    self.drugs[drug][x]["prob"] = prev_stage_val["prob"] * prev_stage_val["succeed_prob"]

                prev_stage_val = self.drugs[drug][x]











