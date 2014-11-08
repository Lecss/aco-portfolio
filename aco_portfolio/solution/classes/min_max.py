from aco import ACO
from graph_wrapper import GraphWrapper
from ant import Ant
import random
import math
from solution import Solution
from sets import Set

class MinMax(ACO):
    def __init__(self, graph_wrapper):
        self.G = graph_wrapper.get_graph()
        self.wrapper = graph_wrapper
        self.ants = []
        self.initialize_pheromones(0.1)
        self.generating = {"A": 5000 , "B": 10000 , "C": 7000, "D": 5000, "E":5000}

        self.best_solution = Solution()

    def run(self, iter_no, ants_no, portfolio_duration):
        self.initialize_ants(ants_no)

        for x in range(0, iter_no):
            for ant in self.ants:

                self.update_capital(ant)
                
                move_to = self.choose_next_node(ant)
                if move_to is not "food":
                    ant.move_next(move_to)
                else:
                    self.terminate_ant(ant, portfolio_duration)
        return self.G

    def update_capital(self,ant):
            path = ant.solution.path

            concurrent = {}
            complete = self.get_complete_drugs(path)["complete"]
            max_time = 0
            
            for node in path:
                if node is not "nest" and node is not "food":
                    drug_name = ''.join([i for i in node if not i.isdigit()])

                    if drug_name in concurrent.keys():
                        concurrent[drug_name] += self.G.node[node]["duration"]
                    else:
                        concurrent[drug_name] = self.G.node[node]["duration"]

                    if concurrent[drug_name] > max_time:
                        max_time = min(concurrent[drug_name], 10)
            
            ant.generated = 0
            for co in complete:
                #if complete then total duration is stored in concurrent
                if concurrent[co] <= max_time:
                    ant.generated += (max_time - concurrent[co]) * self.wrapper.profit_year[co]
                    


    def terminate_ant(self, ant, portfolio_duration):
        new = self.path_expected_value(ant.solution.path, portfolio_duration)
        ant.solution.path.append("food")
        if new > self.best_solution.value:
            self.best_solution.value = new
            self.best_solution.path = ant.solution.path
            self.update_pheromones()

            print self.best_solution.path
            print self.best_solution.value
            print ant.generated


        self.ants.remove(ant)
        self.initialize_ants(1)

    def drug_expected_value(self, drug_key, stages, portfolio_duration):
        accum_pass= 1
        accum_cost = 0
        accum_time = 0
        expected_value = 0

        last_s_key = 0;
        for s_key, stage in stages.iteritems():
            accum_cost += -1 * stage["cost"] 
            accum_time += stage["duration"]
            expected_value += accum_cost * stage["prob"]

            last_s_key = s_key

        expected_value +=  stages[last_s_key]["fail"] * stages[last_s_key]["prob"] * (accum_cost + (self.wrapper.profit_year[drug_key] * (portfolio_duration - accum_time)))
        return expected_value

    def path_expected_value(self, path, portfolio_duration):

        new_drugs = self.get_complete_drugs(path)
        complete = new_drugs["complete"]
        incomplete = new_drugs["incomplete"]
        expected_value = 0

        for key, val in complete.iteritems():
            expected_value += self.drug_expected_value(key,val, portfolio_duration)

        for x in incomplete:
            expected_value -= self.G.node[x]["cost"]

        return expected_value


    def get_complete_drugs(self,path):
        drugs = self.wrapper.get_drugs()

        tmp_drugs = {}
        complete = {}
        remaining = []
        incomplete = []
        for x,y in drugs.iteritems():
            count = 0
            for z,t in y.iteritems():
                if str(x)+str(z) in path:
                    count += 1

            if count == len(y):
                complete[x]=y
            else:
                for z,t in y.iteritems():
                    if str(x)+str(z) in path:
                        incomplete.append(str(x)+str(z))
        
        tmp_drugs["complete"] = complete
        tmp_drugs["incomplete"] = incomplete

        return tmp_drugs


    def initialize_ants(self, ants_no):
        for x in range(ants_no):
            ant = Ant(self.wrapper.nest, self.wrapper.food, self.wrapper.get_graph())
            self.ants.append(ant)

    def initialize_pheromones(self, value=0.1):
        for edge in self.G.edges():
            self.G[edge[0]][edge[1]]["ph"] = value

    def update_pheromones(self):
        solution = self.best_solution

        for edge in self.G.edges():
            best = 0
            if self.G[edge[0]][edge[1]] in solution.path:
                best = 1 / solution.value

            self.G[edge[0]][edge[1]]["ph"] = (1 - ACO.p) * self.G[edge[0]][edge[1]]["ph"] + best

    def choose_next_node(self, ant):
        neighbours = ant.get_neighbours()
        rand = random.random()
        sum_p = 0

        # make sure the food is last chosen
        if len(neighbours) == 0:
            return "food"

        for node in neighbours:
            ph = self.G[ant.curr_node][node]['ph']
            tau = math.pow(ph, ACO.alpha) * math.pow(self.get_heuristic(node), ACO.betha)
            self.G.edge[ant.curr_node][node]["tau"] = tau
            sum_p += tau

        for node in neighbours:
            try:
                if (self.G[ant.curr_node][node]["tau"] / sum_p) > rand:
                    return node
            except:
                pass

        rand2 = random.randint(0, (len(neighbours) - 1))
        return neighbours[rand2]

    def get_heuristic(self, to_node):
        if self.G.node[to_node]['cost'] == 0.0:
            return 0

        niu = 1 / self.G.node[to_node]['cost']
        return niu








