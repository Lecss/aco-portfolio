from solution import Solution
from sets import Set
from time_window import TimeWindow


class Ant():

    ant_id = 0

    def __init__(self, wrapper, portfolio):
        self.solution = Solution()
        self.solution.ant = self
        self.ant_id = Ant.ant_id
        Ant.ant_id += 1
        self.G = wrapper.get_graph()

        self.unavailable = []
        self.not_active = []

        self.curr_node = None
        self.move_next(wrapper.nest)

   
    def populate_inactive(self):
        for x in self.G.nodes():
            node = self.G.node[x]
            if node["active"] != True:
                self.not_active.append(x)

    def move_next(self, node):
        if node is not "food" and node is not "nest":
            self.update_curr_node(node)
        else:
            self.curr_node = node
        
        self.solution.path.append(node)

    def update_curr_node(self,node):
        self.prev_node = self.curr_node
        self.curr_node = node

        self.unavailable.append(self.prev_node)
        self.enable_next_node(node)

    
    def enable_next_node(self, node):
        i = int(node[1:]) + 1
        next_node = str(node[0]) + str(i)

        if next_node in self.not_active:
            self.not_active.remove(next_node)

    def get_neighbours(self):
        sanitized = [item for item in self.G.neighbors(self.curr_node) if item not in self.unavailable and item not in self.not_active]
        return sanitized


