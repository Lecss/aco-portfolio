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
        
        self.best_solution = Solution()

    def run(self, iter_no, ants_no, portfolio_duration):
        self.initialize_ants(ants_no)

        for x in range(0, iter_no):
            for ant in self.ants:
                move_to = self.choose_next_node(ant)

        
                if move_to is "food":
                    ant.move_next(move_to, self.get_complete_drugs(ant.solution.path))
                    self.terminate_ant(ant, portfolio_duration)
                else:
                    ant.move_next(move_to, self.get_complete_drugs(ant.solution.path))

        return self.G


    def terminate_ant(self, ant, portfolio_duration):
        if "food" in ant.solution.path:
            new = self.path_expected_value(ant.solution.path, portfolio_duration)
            #new += ant.generated
            
            if new > self.best_solution.value:
                self.best_solution.value = new
                self.best_solution.path = ant.solution.path
                self.update_pheromones()
                
                if ant.ant_id == 200000:
                    print "----------------------- best solution"
                    print self.best_solution.path
                    #print self.best_solution.value
                    #print (self.get_complete_drugs(ant.solution.path)["complete"]).keys()
                    
                    print 
                    print ant.generated
                    print ant.merged_glob
                    print ant.substracted
                    print ant.position_to_year

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
            ant = Ant(self.wrapper)
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

            ph_value = (1 - ACO.p) * self.G[edge[0]][edge[1]]["ph"] + best

            if ph_value >= solution.value:
                self.G[edge[0]][edge[1]]["ph"] = solution.value
            else:
                self.G[edge[0]][edge[1]]["ph"] = ph_value

    def choose_next_node(self, ant):
        neighbours = ant.get_neighbours()
        rand = random.random()
        sum_p = 0

        # make sure the food is last chosen
        if len(neighbours) > 1 and "food" in neighbours:
            neighbours.remove("food")
        elif len(neighbours) == 1 and "food" in neighbours:
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








