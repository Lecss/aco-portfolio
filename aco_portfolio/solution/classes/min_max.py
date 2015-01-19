from aco import ACO
from graph_wrapper import GraphWrapper
from ant import Ant
import random
import math
from solution import Solution
from sets import Set

class MinMax(ACO):
    def __init__(self, graph_wrapper, portfolio):
        self.wrapper = graph_wrapper
        self.G = self.wrapper.get_graph()
        self.ants = []
        self.initialize_pheromones(0.1)
        self.best_solution = Solution()
        self.portfolio = portfolio
        self.iteration = 0

    def run(self, iter_no, ants_no):
        self.initialize_ants(ants_no)
        portfolio_duration = self.portfolio.model.duration

        for x in range(0, iter_no):
            for ant in self.ants:
                move_to = self.choose_next_node(ant)
                ant.move_next(move_to, self.get_complete_drugs(ant.solution.path))
                    
                if move_to is "food":
                    self.terminate_ant(ant, portfolio_duration)
            self.update_pheromones()
            self.iteration +=1
        return self.G


    def terminate_ant(self, ant, portfolio_duration):

        if "food" in ant.solution.path:
            new = self.path_expected_value(ant, portfolio_duration)

            if new > self.best_solution.value:
                self.best_solution.value = new
                self.best_solution.path = ant.solution.path
                
                print "--------------------------------------------------------------- best solution"
                print self.best_solution.path
                print new
                #print self.best_solution.value
                #print (self.get_complete_drugs(ant.solution.path)["complete"]).keys()
                
                print 
                print "Generated:\t" + str(ant.generated)
                print "Mearged:\t" +  str(ant.merged_glob)
                print "Spent:\t\t" + str(ant.substracted)
                print "When:\t\t" + str(ant.position_to_year)

        self.ants.remove(ant)
        #self.initialize_ants(1)

    def drug_expected_value(self, drug_key, stages, portfolio_duration, ant):
        accum_pass= 1
        accum_cost = 0
        expected_value = 0

        last_s_key = 0;
        for s_key, stage in stages.iteritems():
            accum_cost += -1 * stage["cost"] 
            expected_value += accum_cost * stage["prob"]

            last_s_key = s_key

        years_until_end = portfolio_duration+1 - ant.drugs_so_far[drug_key]

        expected_value +=  accum_cost + (stages[last_s_key]["fail"] * stages[last_s_key]["prob"] * self.wrapper.profit_year[drug_key] * years_until_end )

        return expected_value


    def path_expected_value(self, ant, portfolio_duration):
        path = ant.solution.path
        new_drugs = self.get_complete_drugs(path)
        complete = new_drugs["complete"]
        incomplete = new_drugs["incomplete"]
        expected_value = 0

        for key, val in complete.iteritems():
            expected_value += self.drug_expected_value(key,val, portfolio_duration, ant)

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
            ant = Ant(self.wrapper, self.portfolio)
            self.ants.append(ant)

    def initialize_pheromones(self, value=0.1):
        for edge in self.G.edges():
            self.G[edge[0]][edge[1]]["ph"] = value

    def update_pheromones(self):
        solution = self.best_solution

        for edge in self.G.edges():
            best = 0

            if edge[0] in solution.path and edge[1] in solution.path:
                best = 1 / solution.value

            ph_value = (1 - ACO.p) * self.G[edge[0]][edge[1]]["ph"] + best

            if solution.value is not 0 and ph_value >=  1 / (ACO.p * solution.value):
                self.G[edge[0]][edge[1]]["ph"] = 1 / (ACO.p * solution.value)
            else:
                self.G[edge[0]][edge[1]]["ph"] = ph_value

    def choose_next_node(self, ant):
        neighbours = ant.get_neighbours()
        rand = random.random()
        sum_p = 0

        # make sure the food is last chosen
        if len(neighbours) > 1 and "food" in neighbours:
            if rand > 0.1:
                neighbours.remove("food")
            else:
                return "food"
        elif len(neighbours) == 1 and "food" in neighbours:
            return "food"

        for node in neighbours:
            ph = self.G[ant.curr_node][node]['ph']
            tau = math.pow(ph, ACO.alpha) * math.pow(self.get_heuristic(node), ACO.betha)
            self.G.edge[ant.curr_node][node]["tau"] = tau
            sum_p += tau


        if sum_p == 0:
            print "++++++++++++++++++++++"
            print neighbours
            return neighbours[0]
            print "++++++++++++++++++++++"
        max_tau = 0
        max_node = None

        for node in neighbours:
            if self.G[ant.curr_node][node]["tau"] / sum_p >= max_tau:
                max_node = node
                max_tau = self.G[ant.curr_node][node]["tau"] / sum_p

        return max_node

    def get_heuristic(self, to_node):
        drugs = self.wrapper.get_drugs()
        current_drug = None
        current_drug_key = None

        for x in drugs.keys():
            if x in to_node:
                current_drug = drugs[x]
                current_drug_key = x

        value = 0 
        total_cost = 0
        
        i = 0 
        total_duration = 0 
        for k,v in current_drug.iteritems():
            total_cost += v['cost'] * v["prob"]
            total_duration += v['duration'] 
            i+= 1

        total_cost = self.wrapper.profit_year[current_drug_key] * current_drug[i]['prob'] - total_cost

        #print total_
        niu = (total_cost)/ total_duration 
        return random.randint(0,1000)








