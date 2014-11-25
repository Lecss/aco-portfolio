from solution import Solution
from sets import Set
from time_window import TimeWindow


class Ant():

    ant_id = 0

    def __init__(self, wrapper):
        self.solution = Solution()
        self.curr_node = None
        self.ant_id = Ant.ant_id
        self.wrapper = wrapper
        Ant.ant_id += 1

        self.graph = wrapper.get_graph()
        self.unavailable = Set([])
        self.total_weight = 0
        self.time_invested =  0;

        self.capital = 10000
        self.generated = 0
        self.move_next(wrapper.nest, None)

        self.position_to_year = []
        
    def move_next(self, node, complete):
        self.unavailable.add(self.curr_node)
        self.solution.update_path(node)
        self.curr_node = node
        self.total_weight += self.graph.node[self.curr_node]['cost']

        if complete is not None:
            self.update_time(complete['complete'])


    def update_time(self, complete):
        tmp_capital = self.capital 
        generated_per_year = [0] * 11
        spent_per_year = [0] * 11
        self.position_to_year = [0] * len(self.solution.path)

        for d, d_val in complete.iteritems():
            total_duration = 1
            for s, s_val in d_val.iteritems():
                total_duration += s_val["duration"]

            while total_duration < 11:
                #print self.wrapper.profit_year
                generated_per_year[total_duration] += self.wrapper.profit_year[str(d)]
                total_duration += 1

        i = 0
        drugs_so_far = {}

        for x in self.solution.path:
            if x is "nest" or x is "food":
                i+=1
                continue

            drug = x[:-1]

            if drug not in drugs_so_far.keys():
                drugs_so_far[drug] = 0

            self.position_to_year[i] = drugs_so_far[drug]
            drugs_so_far[drug] += self.graph.node[x]["duration"]

            tmp_capital -= self.graph.node[x]["cost"]
            i+=1


        print tmp_capital
        print 
        print self.solution.path
        # what year does this stage start in
        print self.position_to_year
        

        i =0
        for y in self.position_to_year:
            try:
                stage = self.solution.path[i]
                spent_per_year[y] -= self.graph.node[stage]["cost"]
                i+=1
            except:
                pass

        print generated_per_year
        print spent_per_year
        print 

        merged = [0] * 11
       
        running_total = self.capital
        i = 0
        for x in range(0,11):
            merged[i] = running_total + spent_per_year[i] + generated_per_year[i]
            running_total = merged[i]
            i +=1

        print merged

        print "--------------------"
    def get_weight(self):
        return self.total_weight

    def get_neighbours(self):
        neigh = self.graph.neighbors(self.curr_node)
        sanitized = []

        for x in neigh:
            if x not in self.solution.path and x not in self.unavailable:
                #TEST FOR EMPTY NODE{X} => node[x] = {}
                if self.graph.node[x]['cost'] + self.total_weight <= self.capital + self.generated:
                    sanitized.append(x)

        return sanitized


