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

        self.capital = 15000
        self.generated = 0
        self.move_next(start)

    def move_next(self, node):
        self.solution.update_path(node)
        self.curr_node = node
        self.total_weight += self.graph.node[self.curr_node]['cost']


    def get_weight(self):
        return self.total_weight

    def get_neighbours(self):
        neigh = self.graph.neighbors(self.curr_node)
        sanitized = []

        for x in neigh:
            if x not in self.solution.path and x not in self.unavailable:
                #TEST FOR EMPTY NODE{X} => node[x] = {}

                if self.ant_id ==0 :
                    pass
                    #print str(x) + "cost: " + str(self.graph.node[x]['cost']) + " -- weight:" + str(self.total_weight)

                if self.graph.node[x]['cost'] + self.total_weight <= self.capital + self.generated:
                    sanitized.append(x)
        sanitized.remove("food")
        return sanitized