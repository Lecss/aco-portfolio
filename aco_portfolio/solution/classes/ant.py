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
        self.substracted = [0] * 11

        self.extra = []
        self.last_year = 0

        self.move_next(wrapper.nest, None)
        """ self.move_next("L2", None)"""

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


            wait = 0 

            if x in self.extra:
                wait += self.last_year

            self.position_to_year[i] =  drugs_so_far[drug]
            if wait != 0:
                drugs_so_far[drug] +=  wait - drugs_so_far[drug] + self.graph.node[x]["duration"]
            else:
                drugs_so_far[drug] += self.graph.node[x]["duration"]

            tmp_capital -= self.graph.node[x]["cost"]
            i+=1


        if self.ant_id == 2000000:
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
        if self.ant_id == 20000000:
            print generated_per_year
            print spent_per_year
            print 

        merged = [0] * 11
       
        running_total = self.capital
        i = 0
        self.substracted = [0] * 11
        for x in range(0,11):
            merged[i] = running_total + spent_per_year[i] + generated_per_year[i]
            running_total = merged[i]

            self.substracted[i] = generated_per_year[i] + spent_per_year[i]
            i +=1

        self.generated = generated_per_year
        if self.ant_id == 2000000:
            print merged
            print self.substracted

            print "--------------------"
    def get_weight(self):
        return self.total_weight

    def get_neighbours(self):
        neigh = self.graph.neighbors(self.curr_node)
        sanitized = []

        for x in neigh:
            if x not in self.solution.path and x not in self.unavailable:
                #TEST FOR EMPTY NODE{X} => node[x] = {}
                if self.graph.node[x]['cost'] + self.total_weight <= self.capital:
                    sanitized.append(x)

        for x in neigh:
            if x not in self.solution.path and x not in self.unavailable:
                i = 0 
                if (len(sanitized) == 0 or (len(sanitized) == 1 and "food" in sanitized)):
                    available = self.capital - sum(self.substracted)
                   
                    while (self.substracted[i] < 1) and i< 10:
                        i+=1

              
                if self.graph.node[x]["cost"] < self.substracted[i]: 
                    sanitized.append(x)
                    self.extra.append(x)
                    self.last_year = i

        return sanitized


