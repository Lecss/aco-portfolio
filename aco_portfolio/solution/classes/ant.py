from solution import Solution
from sets import Set
from time_window import TimeWindow


class Ant():

    ant_id = 0

    def __init__(self, start, end, graph):
        self.solution = Solution()
        self.curr_node = None
        self.ant_id = Ant.ant_id
        Ant.ant_id += 1

        self.graph = graph
        self.unavailable = Set([])
        self.total_weight = 0
        self.time =  0;

        self.capital = 9500
        self.generated = 0
        self.move_next(start)

        self.cc = {}

    def move_next(self, node):
        self.unavailable.add(self.curr_node)
        self.solution.update_path(node)
        self.curr_node = node
        self.total_weight += self.graph.node[self.curr_node]['cost']

    def update_capital(self, complete, time, profit_year):
            path = self.solution.path

            concurrent = {}
            complete = complete
            max_time = 0
            
            for node in path:
                if node is not "nest" and node is not "food":
                    drug_name = ''.join([i for i in node if not i.isdigit()])

                    if drug_name in concurrent.keys():
                        concurrent[drug_name] += self.graph.node[node]["duration"]
                    else:
                        concurrent[drug_name] = self.graph.node[node]["duration"]

                    if concurrent[drug_name] > max_time:
                        max_time = min(concurrent[drug_name], time)
            
            self.generated = 0
            for co in complete:
                #if complete then total duration is stored in concurrent
                self.generated += (max_time - concurrent[co]) * profit_year[co]

                if "food" in path:
                   self.generated += (time - max_time) * profit_year[co] 



    def get_weight(self):
        return self.total_weight

    def get_neighbours(self):
        neigh = self.graph.neighbors(self.curr_node)
        sanitized = []

        for x in neigh:
            if x not in self.solution.path and x not in self.unavailable:
                #TEST FOR EMPTY NODE{X} => node[x] = {}

                if self.ant_id == 20: 
                   print str(x) + ":"+str(self.graph.node[x]['cost']) +  ":" + str(self.total_weight) + "<=" + str(self.capital) + ":" + str(self.generated)

                if self.graph.node[x]['cost'] + self.total_weight <= self.capital + self.generated:
                    sanitized.append(x)
        sanitized.remove("food")
        return sanitized


