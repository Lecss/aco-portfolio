from aco import ACO
from graph_wrapper import GraphWrapper
from ant import Ant
import random
import math
from solution import Solution
from sets import Set
import time
from expected_value import ExpectedValue
import json

class MinMax(ACO):
    def __init__(self, graph_wrapper, portfolio):
        self.wrapper = graph_wrapper
        self.G = graph_wrapper.get_graph()
        self.ants = []

        self.experience = {}

        self.expected_value = ExpectedValue(self.G, portfolio)

        self.initialize_pheromones()
        self.best_solution_vector = []

        self.portfolio = portfolio
        self.start_time = time.time()

    def initialize_pheromones(self):
        value = 10
        for edge in self.G.edges():
            self.G[edge[0]][edge[1]]["ph"] = value
            self.G[edge[0]][edge[1]]["from"] = edge[0] + ":" +  edge[1]
 
        for node in self.G.nodes():
            self.G.node[node]["ph"] = 100
        return

    def initialize_ants(self, ants_no):
        for x in range(ants_no):
            ant = Ant(self.wrapper, self.portfolio)
            self.ants.append(ant)

    def terminate_ant(self, ant):
        #entering upon food being the ant's current node 
        if len(ant.solution.path) > 2:
            #print ant.solution.path
            #ant.solution.path = path = ["nest","L1","L2","C1","J1","H1","I1","C2","I2","H2","G1", "H3","K1","K2", "K3","D1","D2","J2","A1","A2","D3", "J3","A3","G2","food" ] 
            solution_value = self.path_expected_value(ant.solution.path)

            ant.solution.value = solution_value
            ant.time = time.time() - self.start_time
            ant.solution.years = json.loads(json.dumps(self.expected_value.years_()))
            ant.solution.budget_over_years = [self.expected_value.years[x]["budget"] for x in self.expected_value.years]
            #init and maintain the solutions vector
            if len(self.best_solution_vector) == 0:
                self.best_solution_vector.append(ant.solution)
            else:
                index = 0
                min_value = self.best_solution_vector[index].value

                for best_sol in self.best_solution_vector:
                    if best_sol.value < min_value:
                        min_value = best_sol.value
                        index = self.best_solution_vector.index(best_sol)

                if solution_value > min_value:
                    if len(self.best_solution_vector) > 2:
                        self.best_solution_vector.pop(index)
                    #print ant.solution.path
                    #print ant.solution.value
                    #print "============"
                    self.best_solution_vector.append(ant.solution)

        self.ants.remove(ant)
        self.initialize_ants(1)

    def run(self, iter_no, ants_no):
        self.initialize_ants(ants_no)

        for x in range(0, iter_no):
            for ant in self.ants:
                self.build_ant_solution(ant)
                self.update_local_pheromones(ant)
            self.daemon()
            self.update_pheromones()
        return self.G

    def build_ant_solution(self, ant):
        while ant.curr_node is not ACO.food:
            next_node = self.choose_next_node(ant.curr_node, ant)
            ant.move_next(next_node)

        self.terminate_ant(ant)

    def path_expected_value(self, path):
        return self.expected_value.compute(path)

    def daemon(self):
        pass

    def update_pheromones(self):
        for sol in self.best_solution_vector:
            path = sol.path
            
            for node in self.G.nodes():
                ph = self.G.node[node]["ph"]
                self.G.node[node]["ph"] = max(1-ACO.p * ph, 0.5)

                exclude = node is not ACO.food and node is not ACO.nest and self.G.node[node]["last_stage"] not in path

                if node in path and not exclude:
                    self.G.node[node]["ph"] += (len(path) - path.index(node)) * (self.G.node[node]["index"] + 1)

                  

                    """
                    #AASDSAKDKSADLMSALDNSA:LDNLSA:NDSA:ND HARDCODE YEAR
                    if node in sol.years["12"]["items"] or node in sol.years["11"]["items"]:
                        first_node =  self.G.node[node]["start_stage"]
                        self.G.node[first_node]["ph"] = 0.5"""

    def update_local_pheromones(self, ant):
        pass

    def choose_next_node(self, curr_node, ant):
        neighbours = ant.get_neighbours()
        fitnesses = []

        #return neighbours[random.randint(0, len(neighbours) - 1)]
        for node in neighbours:
            ph = self.G.node[node]["ph"]

            tau = math.pow(ph, ACO.alpha) * math.pow(self.get_heuristics(node, ant.solution.path), ACO.betha)
            self.G.edge[curr_node][node]["tau"] = tau
            fitnesses.append(tau)

        selection = self.roulette_select(neighbours, fitnesses, len(neighbours))
        return selection[random.randint(0, len(selection) - 1)]

    def get_heuristics(self, node, path):
        #return 1
        if node is ACO.food:
            return 1500

        #time_heuristic = self.time_heuristic(node, path)
        time_heuristic = 1

        #print self.G.node[node]["drug"]["cummulated_prob"] * self.G.node[node]["drug"]["profit_per_year"] * time_heuristic

        return self.G.node[node]["drug"]["cummulated_prob"] * self.G.node[node]["drug"]["profit_per_year"] * time_heuristic

    def time_heuristic(self,node, path):
        exp_val = ExpectedValue(self.G, self.portfolio, path)
        invested_in = exp_val.add_to_year(node, True)

        """
        if "A" in node:
            print invested_in
            print path
            print "============"
        """
        drug_total_duration = self.G.node[node]["drug"]["total_duration"]
        return self.portfolio.model.duration - (drug_total_duration + invested_in)


    def roulette_select(self, population, fitnesses, num):
        """ Roulette selection, implemented according to:
            <http://stackoverflow.com/questions/177271/roulette
            -selection-in-genetic-algorithms/177278#177278>
            http://stackoverflow.com/questions/298301/roulette-wheel-selection-algorithm"""

        total_fitness = float(sum(fitnesses))
        rel_fitness = [f / total_fitness for f in fitnesses]
        # Generate probability intervals for each individual
        probs = [sum(rel_fitness[:i + 1]) for i in range(len(rel_fitness))]
        # Draw new population
        new_population = []
        for n in xrange(num):
            r = random.random()
            for (i, individual) in enumerate(population):
                if r <= probs[i]:
                    new_population.append(individual)
                    break
        return new_population

    def record(self,ant):
        key = ""
        for x in ant.solution.path:
            key+= x
            #print key
            if key not in self.experience:
                self.experience[key] = ant.solution.value

















