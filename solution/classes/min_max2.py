from aco import ACO
from graph_wrapper import GraphWrapper
from ant import Ant
import random
import math
from solution import Solution
from sets import Set
import time


class MinMax(ACO):
    def __init__(self, graph_wrapper, portfolio):
        self.wrapper = graph_wrapper
        self.G = self.wrapper.get_graph()
        self.ants = []
        self.initialize_pheromones()
        self.best_solution_vector = []
        self.portfolio = portfolio
        self.iteration = 0
        self.solutions_found = []
        self.start_time = time.time()
        self.count = 0

    def initialize_pheromones(self):
        value = 100
        for edge in self.G.edges():
            self.G[edge[0]][edge[1]]["ph"] = value
            self.G[edge[0]][edge[1]]["from"] = edge[0] + ":" +  edge[1]

            #self.G["M1"]["M2"]["ph"] = 1
        return

    def run(self, iter_no, ants_no):
        self.initialize_ants(ants_no)

        for x in range(0, iter_no):
            for ant in self.ants:
                self.build_ant_solution(ant)
                self.update_local_pheromones(ant)
            self.daemon()
            self.update_pheromones()
            print self.count
        return self.G

    def build_ant_solution(self, ant):
        while ant.curr_node is not ACO.food:
            next_node = self.choose_next_node(ant.curr_node, ant)
            ant.move_next(next_node, self.get_complete_drugs(ant.solution.path))

        self.terminate_ant(ant)


    def terminate_ant(self, ant):
        if len(ant.solution.path) > 2:
            solution_value = self.path_expected_value(ant.solution.path, ant.so_far)
            ant.solution.value = solution_value
            ant.time = time.time() - self.start_time

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

    def drug_expected_value(self, drug_key, stages, drugs_so_far):
        portfolio_duration = self.portfolio.model.duration
        accum_pass = 1
        accum_cost = 0
        expected_value = 0

        last_s_key = 0;
        for s_key, stage in stages.iteritems():
            accum_cost += -1 * stage["cost"]
            expected_value += accum_cost * stage["prob"]

            last_s_key = s_key

        years_until_end = portfolio_duration + 1 - drugs_so_far
        expected_value += accum_cost + (
        stages[last_s_key]["succeed_prob"] * stages[last_s_key]["prob"] * self.wrapper.profit_year[drug_key] * years_until_end )

        return expected_value

    def path_expected_value(self, path, drugs_so_far):
        new_drugs = self.get_complete_drugs(path)

        complete = new_drugs["complete"]
        incomplete = new_drugs["incomplete"]
        expected_value = 0

        for key, val in complete.iteritems():
            expected_value += self.drug_expected_value(key, val, drugs_so_far[key])

        for x in incomplete:
            expected_value -= self.G.node[x]["cost"]

        return expected_value

    def daemon(self):
        pass

    def update_pheromones(self):
        for solution in self.best_solution_vector:
            for edge in self.G.edges():
                best = 0

                

                if edge[0] in solution.path and edge[1] in solution.path:
                    time_left = self.time_left_heuristic(edge, solution.ant)
                    #time_left = 0
                    index = solution.path.index(edge[1])
                    #print self.G[edge[0]][edge[1]]["ph"]
                    #print self.G[edge[0]][edge[1]]
                    best = 1 / solution.value + time_left

                ph_value = (1 - ACO.p) * self.G[edge[0]][edge[1]]["ph"] + best

                self.G[edge[0]][edge[1]]["ph"] = ph_value


    """def update_local_pheromones(self, ant):
        solution = ant.solution
        for node in solution.path:
            if node is ACO.food or node is ACO.nest:
                continue

            if "ph" not in self.G.node[node]:
                self.G.node[node]['ph'] = {}

            #compute time left till end 
            year = ant.position_to_year[solution.path.index(node)]

            time_left = 0
            if "1" in node:
                time_left = self.portfolio.model.duration - (self.G.node[node]["drug"]["total_duration"] + year)
            elif "2" in node:
                pass#time_left = self.portfolio.model.duration - 
            
            if "A1" in node:
                print year
                print self.G.node[node]['ph']
            

            #compute expected value given time left
            expect_per_year = self.G.node[node]["drug"]["profit_per_year"]
            time_profit = time_left * expect_per_year
            time_profit_risk = time_profit * self.G.node[node]["drug"]["cummulated_prob"]
            
            self.G.node[node]['ph'][year] = time_profit_risk


            if "A1" in node:
                print self.G.node[node]['ph']
                print "+++++++++++++++++"
    """

    def update_local_pheromones(self,ant):
        solution = ant.solution
        for node in solution.path:
            if node is ACO.food or node is ACO.nest:
                continue

            if "ph" not in self.G.node[node]:
                self.G.node[node]['ph'] = {}

            year = 1

            for x in ant.years:
                if node in ant.years[x]["items"]:
                    year = x
                    break 

            self.G.node[node]['ph'][year] = ant.solution.value


    def time_left_heuristic(self, edge, ant):
        path = ant.solution.path
        
        edge_0_time =  0   
        edge_1_time =  0 


        for x in ant.years:
            if edge[0] in ant.years[x]["items"]:
                edge_0_time = x
            if edge[1] in ant.years[x]["items"]:
                edge_1_time = x

        to = edge[1] if edge_0_time < edge_1_time else edge[0]

        if to is ACO.food or to is ACO.nest:
            return 0
        #print self.G.node[to]
        #print to
        time_left = self.portfolio.model.duration - self.G.node[to]["drug"]["total_duration"]

        #print time_left
        if time_left is 0:
            return 0

        return  1 / time_left

    def choose_next_node(self, curr_node, ant):
        neighbours = ant.get_neighbours()
        rand = random.random()
        fitnesses = []
        
        # return neighbours[random.randint(0, len(neighbours)-1)]
        for node in neighbours:
            node_ph = 0
            
            if node is not ACO.food:
                year = ant.get_year(node)

            if "ph" in self.G.node[node] and str(year) in self.G.node[node]["ph"]:
                if year < self.portfolio.model.duration:    
                    node_ph = 1 / self.G.node[node]['ph'][year]
                else:
                    start_node = self.G.node[node]["start_node"]
                    start_node = self.G.node[start_node]

                    node_ph = -1

            ph = self.G[curr_node][node]['ph'] + node_ph
            tau = math.pow(ph, ACO.alpha) * math.pow(1, ACO.betha)
            self.G.edge[curr_node][node]["tau"] = tau
            fitnesses.append(tau)

        selection = self.roulette_select(neighbours, fitnesses, len(neighbours))
        return selection[random.randint(0, len(selection) - 1)]

    def get_heuristic(self, node):
        drug = self.G.node[node]["drug"]["name"]
        stage = self.G.node[node]["index"]

        if node is ACO.food:
            return 0.0002
        niu = 1 / drug["cost"] * stage *  1 / drug["duration"]

        return niu


    def roulette_select(self, population, fitnesses, num):
        """ Roulette selection, implemented according to:
            <http://stackoverflow.com/questions/177271/roulette
            -selection-in-genetic-algorithms/177278#177278>
        """
        """http://stackoverflow.com/questions/298301/roulette-wheel-selection-algorithm"""

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


    def get_complete_drugs(self, path):
        result = {}
        result["complete"] = {}
        result["incomplete"] = []
        tmp_complete_stages = []

        for stage in path:
            if stage is not ACO.food and stage is not ACO.nest:
                stages_no =  self.G.node[stage]["drug"]["stages_count"]
                parent_drug = self.G.node[stage]["drug"]["name"]

                if parent_drug + str(stages_no) in path:
                    result["complete"][parent_drug] = self.wrapper.drugs[parent_drug]
                    i = 1
                    while i <= stages_no:
                        tmp_complete_stages.append(str(parent_drug) + str(i))
                        i += 1

        result["incomplete"] = list(set(path) - set(tmp_complete_stages))

        return result

    def initialize_ants(self, ants_no):
        for x in range(ants_no):
            ant = Ant(self.wrapper, self.portfolio)
            self.ants.append(ant)




















