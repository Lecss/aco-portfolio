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

    def initialize_pheromones(self):
   		value = 1
   		for edge in self.G.edges():
   			self.G[edge[0]][edge[1]]["ph"] = value

   		return 
   			

    def run(self, iter_no, ants_no):
        self.initialize_ants(ants_no)

        for x in range(0, iter_no):
        	for ant in self.ants:
        		self.build_ant_solution(ant)
        	self.daemon()
        	self.update_pheromones()
        return self.G

    def build_ant_solution(self, ant):
    	while ant.curr_node is not ACO.food:
    		next_node = self.choose_next_node(ant.curr_node, ant.get_neighbours())
    		ant.move_next(next_node, self.get_complete_drugs(ant.solution.path))

    	self.terminate_ant(ant)


    def terminate_ant(self, ant):
    	if len(ant.solution.path) > 2:
	    	solution_value = self.path_expected_value(ant.solution.path, ant.drugs_so_far)
	    	ant.solution.value = solution_value
	    	ant.time = time.time() - self.start_time
	    	#print ant.solution.path
	    	#print solution_value
	    
	    	#print "-----"

	    	if len(self.best_solution_vector) < 2:
	    		self.best_solution_vector.append(ant.solution)
	    		self.solutions_found.append(ant.solution)
	    	else:
	    		i = 0
	    		min_value = self.best_solution_vector[i].value

	    		for sol in self.best_solution_vector:
	    			if sol.value < min_value:
	    				min_value = sol.value
	    				i = self.best_solution_vector.index(sol)

	    		self.best_solution_vector.pop(i)


	    	for sol in self.best_solution_vector:
	    		if solution_value > sol.value:
	    			self.best_solution_vector.append(ant.solution)
	    			self.solutions_found.append(ant.solution)

    	self.ants.remove(ant)
    	self.initialize_ants(1)

    def drug_expected_value(self, drug_key, stages, drugs_so_far):
    	portfolio_duration = self.portfolio.model.duration
    	accum_pass= 1
        accum_cost = 0
        expected_value = 0

        last_s_key = 0;
        for s_key, stage in stages.iteritems():
            accum_cost += -1 * stage["cost"] 
            expected_value += accum_cost * stage["prob"]

            last_s_key = s_key

        years_until_end = portfolio_duration + 1 - drugs_so_far
        expected_value +=  accum_cost + (stages[last_s_key]["fail"] * stages[last_s_key]["prob"] * self.wrapper.profit_year[drug_key] * years_until_end )

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
	                index = solution.path.index(edge[1])
	                best = 1 / solution.value 

	            ph_value = (1 - ACO.p) * self.G[edge[0]][edge[1]]["ph"] + best


    def choose_next_node(self, curr_node, neighbours):
    	rand = random.random()
    	fitnesses = []
    	
    	#return neighbours[random.randint(0, len(neighbours)-1)]
    	for node in neighbours:
            ph = self.G[curr_node][node]['ph']
            tau = math.pow(ph, ACO.alpha) * math.pow(self.get_heuristic(node), ACO.betha)
            self.G.edge[curr_node][node]["tau"] = tau
            fitnesses.append(tau)

        selection = self.roulette_select(neighbours, fitnesses, len(neighbours))
        return selection[random.randint(0,len(selection)-1)]

    def get_heuristic(self, node):
    	drug = node[:1]
    	stage = node[1:]

    	#print self.wrapper.get_drugs()[drug]

    	if node is ACO.food:
    		#return 0.0002
    		return 0.0002
    	niu = 1/ self.wrapper.get_drugs()[drug][int(stage)]["cost"] * int(stage) *  1/ self.wrapper.get_drugs()[drug][int(stage)]["duration"]
    	
    	print str(node) + ":" + str(round(niu,4))
    	return niu


    def roulette_select(self, population, fitnesses, num):
        """ Roulette selection, implemented according to:
            <http://stackoverflow.com/questions/177271/roulette
            -selection-in-genetic-algorithms/177278#177278>
        """
        """http://stackoverflow.com/questions/298301/roulette-wheel-selection-algorithm"""

        total_fitness = float(sum(fitnesses))
        rel_fitness = [f/total_fitness for f in fitnesses]
        # Generate probability intervals for each individual
        probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
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
    	drugs = self.wrapper.get_drugs()
    	drug_stage_map = self.wrapper.drug_stages
    	result = {}
    	result["complete"] = {}
    	result["incomplete"] = []
    	tmp_complete_stages = []

    	for drug_name, drug_stages_no in drug_stage_map.iteritems():
    		if str(drug_name) + str(drug_stages_no) in path:
    			result["complete"][drug_name] = drugs[drug_name]
    			i = 1
    			while i <= drug_stages_no:
    				tmp_complete_stages.append(str(drug_name) + str(i))
    				i+=1

    	result["incomplete"] = list(set(path) - set(tmp_complete_stages))

    	return result

    def initialize_ants(self, ants_no):
    	for x in range(ants_no):
            ant = Ant(self.wrapper, self.portfolio)
            self.ants.append(ant)




















