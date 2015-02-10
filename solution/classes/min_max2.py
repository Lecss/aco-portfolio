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
                    if len(self.best_solution_vector) > 1:
                        self.best_solution_vector.pop(index)
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
        path = self.best_solution_vector[0].path
        for node in self.G.nodes():
            ph = self.G.node[node]["ph"]
            self.G.node[node]["ph"] = max(1-ACO.p * ph, 0.5)


    def update_local_pheromones(self, ant):
        pass

    def choose_next_node(self, curr_node, ant):
        neighbours = ant.get_neighbours()
        fitnesses = []

        for node in neighbours:
            tau = math.pow(1, ACO.alpha) * math.pow(1, ACO.betha)
            self.G.edge[curr_node][node]["tau"] = tau
            fitnesses.append(tau)

        selection = self.roulette_select(neighbours, fitnesses, len(neighbours))
        return selection[random.randint(0, len(selection) - 1)]

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

















