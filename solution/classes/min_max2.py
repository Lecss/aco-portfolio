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
import time
import copy
import operator

class MinMax(ACO):
    def __init__(self, graph_wrapper, portfolio, partial_sol=[], failed=[]):
        self.wrapper = graph_wrapper
        self.G = graph_wrapper.get_graph()
        self.ants = []
        self.partial_sol = partial_sol
        self.failed = failed
        self.experience = {}

        self.expected_value = ExpectedValue(self.G, portfolio, partial_sol, failed)
        self.pheromones = {}

        self.calculated_solutions =[]
        self.initialize_pheromones()
        self.best_solution_vector = []
        self.best_drugs_by_ratio = self.get_best_drugs()
        self.tmp_years = {}
        self.portfolio = portfolio
        self.start_time = time.time()
        self.solution_full = {}

    def initialize_pheromones(self):
        value = 1
        for edge in self.G.edges():
            self.G[edge[0]][edge[1]]["ph"] = value
            self.G[edge[0]][edge[1]]["from"] = edge[0] + ":" +  edge[1]
 
        for node in self.G.nodes():
            self.G.node[node]["ph"] = 40
        return

    def initialize_ants(self, ants_no):
        for x in range(ants_no):
            ant = Ant(self.wrapper, self.portfolio, self.partial_sol, self.failed)
            self.ants.append(ant)

    def get_best_drugs(self):
        best = {}

        for node in self.G:
            if node is not ACO.food and node is not ACO.nest:
                drug = self.G.node[node]["drug"]
                drug_name = drug["name"]
                ratio = self.get_drug_ratio(drug)

                best[drug_name] = ratio

        sorted_best = sorted(best.items() , key=operator.itemgetter(1), reverse=True)
    
        return sorted_best

    def get_drug_ratio(self, drug):
        cummulated_prob = drug["cummulated_prob"]
        duration = drug["total_duration"]
        profit = drug["profit_per_year"]
        cost = drug["total_cost"]

        
        #print cummulated_prob * 1/duration * profit
        return cummulated_prob * 1/duration * (profit - cost)
        
    def switch_path(self,ant):
        drug = self.next_best_drugs_by_ratio(ant.solution.path)
        initial_stage = drug[0] + "1"
        complement = self.expected_value.get_stage_complement(initial_stage)

        new_path = list(ant.solution.path)
        new_path += [initial_stage] + complement
        new_path_prepend =  [initial_stage] + complement + list(ant.solution.path)

        e1 = self.expected_value.compute(new_path)
        e2 = self.expected_value.compute(ant.solution.path)
        e3 = self.expected_value.compute(new_path_prepend)

        l = [e1,e2,e3]
        max_val = max(l)

        index = l.index(max_val)

        if index == 0:
            ant.solution.path = new_path
        elif index == 2: 
            ant.solution.path = new_path_prepend


    def terminate_ant(self, ant):
        #entering upon food being the ant's current node 
        if len(ant.solution.path) > 2:
    
            ant.solution.path.pop()
            ant.solution.path.pop(0)
            solution_value = 0
            #self.switch_path(ant)
            years = None
            #memoization
            if str(ant.solution.path) not in self.calculated_solutions:
                for x in ant.solution.path:
                    solution_value += self.path_expected_value2(ant.solution.path,x,[])

                self.tmp_years = copy.deepcopy(self.expected_value.years)
                years = self.tmp_years

                self.calculated_solutions.append(str(ant.solution.path))


                ant.solution.path = ant.solution.path
                ant.solution.value = solution_value / len(self.solution_full)
                ant.time = time.time() - self.start_time
                ant.solution.years = json.loads(json.dumps(years))
                ant.solution.budget_over_years = [years[x]["budget"] for x in years]

                ant.solution.full_vector = copy.deepcopy(self.solution_full)
                self.solution_full = {}
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

        print "LEN"
        print len(self.calculated_solutions)
        return self.G

    def build_ant_solution(self, ant):
        while ant.curr_node is not ACO.food:
            next_node = self.choose_next_node(ant.curr_node, ant)
            ant.move_next(next_node)

        self.terminate_ant(ant)

    def path_expected_value2(self, path, failing_now, acummulated=[]):
        index_failing = path.index(failing_now)

        local_acummulated = list(acummulated)
        local_acummulated.append(failing_now)

        rm = []
        for i in local_acummulated:
            l = self.wrapper.get_drug_stages(self.G.node[i]["drug"]["name"])
            if i in l and failing_now in l and i != failing_now:
                rm.append(i)

        for i in rm:
            local_acummulated.remove(i)
            
        alts = self.get_alternatives_for_stage_fail(path, failing_now)
        max_val = 0
        max_path = []

        for sub_path in alts:
            tmp_val = self.expected_value.compute(sub_path, local_acummulated)
            if len(max_path) == 0 and (tmp_val != None):
                max_path = sub_path
                max_val = tmp_val

            if tmp_val > max_val:
                max_val = tmp_val
                max_path = sub_path

        
        #print str(path) + " : " + str(local_acummulated) + " : " + str(max_val)

        self.solution_full[str(list(local_acummulated))] = { "path": list(max_path), "value": max_val}

        if len(max_path) == 0:
            return self.expected_value.min_so_far


        for x in max_path:
            if index_failing < max_path.index(x):
                tmp = self.path_expected_value2(max_path, x, local_acummulated)

                if tmp is None: 
                    return 0
                else:
                    max_val += tmp

        return max_val


    def next_best_drugs_by_ratio(self, path):
        arr =[]

        for x in self.best_drugs_by_ratio:
            drug_name = x[0]
            stage = drug_name + "1"
            if stage in path:
                continue
            else:
                if (len(arr) < 1):
                    arr.append(drug_name)
        return arr

    def get_alternatives_for_stage_fail(self, path, stage_failing):
        tmp_best = self.next_best_drugs_by_ratio(path)
        add = []

        for x in tmp_best:
            stages = self.wrapper.get_drug_stages(x)
            add.append(stages)
        
        alt_paths = []
        tmp_path = list(path)

        drug_name = self.G.node[stage_failing]["drug"]["name"]
        for x in path:
            if self.G.node[x]["drug"]["name"] == drug_name and self.G.node[x]["index"] > self.G.node[stage_failing]["index"]:
                tmp_path.remove(x)

        for l in add:
            if stage_failing not in l and l[0] not in path: 
                tmp =[]
                tmp += tmp_path
                tmp += l
                alt_paths.append(tmp)

        alt_paths.append(tmp_path)
        return alt_paths

    def daemon(self):
        pass

    def update_pheromones(self):
        path =  None
        best_value = -1000000
        for sol in self.best_solution_vector:
            path = sol.path
            if sol.value > best_value:
                path = sol.path
                best_value = sol.value

        for node in self.G.nodes():
            #evaporate
            ph = max((1-ACO.p) * self.G.node[node]["ph"], 1)
            self.G.node[node]["ph"] = ph

            exclude = node is ACO.food or node is ACO.nest or self.G.node[node]["last_stage"] not in path

            if node in path and not exclude:
                #print "ebtreertreter"
                # index logic = the higher the index the more important to finish it
                self.G.node[node]["ph"] += (len(path) - path.index(node)) * (self.G.node[node]["index"] + 1)

            if node in self.pheromones.keys():
                self.pheromones[node].append(self.G.node[node]["ph"])
            else:
                self.pheromones[node] = [self.G.node[node]["ph"]]

            for edge in self.G.edges():
                self.G.edge[edge[0]][edge[1]]["ph"] =  max((1-ACO.p) * self.G.edge[edge[0]][edge[1]]["ph"], 1)

            for x in range(0, len(path)-1):
                val = sol.value if sol.value != None and sol.value != 0 else 1
                self.G.edge[path[x]][path[x+1]]["ph"] =  self.G.edge[path[x]][path[x+1]]["ph"] * (1 - 1/val)

    def update_local_pheromones(self, ant):
        pass

    def choose_next_node(self, curr_node, ant):
        neighbours = ant.get_neighbours()
        fitnesses = []

        #return neighbours[random.randint(0, len(neighbours) - 1)]
        for node in neighbours:
            ph = self.G.node[node]["ph"]
            ph2 = self.G.edge[curr_node][node]["ph"]

            tau = math.pow(ph+ph2, ACO.alpha) * math.pow(self.get_heuristics(curr_node, node, ant.solution.path), ACO.betha)
            self.G.edge[curr_node][node]["tau"] = tau
            fitnesses.append(tau)

        selection = self.roulette_select(neighbours, fitnesses, len(neighbours))
        return selection[random.randint(0, len(selection) - 1)]

    def get_heuristics(self, curr_node, node, path):
        #return 1
        if node is ACO.food:
            return 600

        #time_heuristic = self.time_heuristic(node, path)

        return self.G.node[node]["drug"]["cummulated_prob"] * self.G.node[node]["drug"]["profit_per_year"] * 1/self.G.node[node]["drug"]["total_duration"]

    def time_heuristic(self,node, path):
        exp_val = ExpectedValue(self.G, self.portfolio, path)
        invested_in = exp_val.add_to_year(node, True)

        drug_total_duration = self.G.node[node]["drug"]["total_duration"]
        return self.portfolio.model.duration - (drug_total_duration + invested_in)

    def roulette_select(self, population, fitnesses, num):
        """ Roulette selection """

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

















