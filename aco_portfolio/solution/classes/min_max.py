from aco import ACO
from graph_wrapper import GraphWrapper
from ant import Ant
import random
import math
from solution import Solution


class MinMax(ACO):
    def __init__(self, graph_wrapper):
        self.G = graph_wrapper.get_graph()
        self.wrapper = graph_wrapper
        self.ants = []
        self.initialize_pheromones(0.1)
        self.generating = {"A": 5000 *5, "B": 10000 *6, "C": 7000*8, "D": 5000*10, "E":5000*5}

        self.best_solution = Solution()

    def run(self, iter_no, ants_no):
        self.initialize_ants(ants_no)

        for x in range(0, iter_no):
            for ant in self.ants:
                move_to = self.choose_next_node(ant)
                if move_to != -1:
                    ant.move_next(move_to)
                else:
                    self.terminate_ant(ant)
        return self.G

    def terminate_ant(self, ant):
        new = self.expected_value(ant.solution.path)

        if new > self.best_solution.value:
            self.best_solution.value = new
            self.best_solution.path = ant.solution.path
            self.update_pheromones()

            print self.best_solution.path
            print self.best_solution.value

        self.ants.remove(ant)
        self.initialize_ants(1)

    def expected_value(self, path):
        drugs = self.wrapper.get_drugs()
        #r =  self.compute_expected(drugs["E"], 1)

        new_drugs = {}
        for x,y in drugs.iteritems():
            count = 0
            for z,t in y.iteritems():
                if str(x)+str(z) in path:
                    count += 1

            if count == len(y):
                new_drugs[x]=y


        expected_value = 0
        for key, val in new_drugs.iteritems():
            accum_pass= 1
            accum_cost = 0
            for s_key, stage in val.iteritems():
                accum_pass *= stage["fail"]
                accum_cost += -1 * stage["cost"] * accum_pass
                expected_value += accum_pass * accum_cost

            expected_value += accum_pass * drugs[key][len(drugs[key])]["fail"] *  self.generating[key]
        return expected_value

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
        if len(neighbours) != 1 and "food" in neighbours:
            neighbours.remove("food")

        if len(neighbours) == 0:
            return -1

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








