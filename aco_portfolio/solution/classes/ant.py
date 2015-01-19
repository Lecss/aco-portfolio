from solution import Solution
from sets import Set
from time_window import TimeWindow


class Ant():

    ant_id = 0
    print_id = -1

    def __init__(self, wrapper, portfolio):
        self.solution = Solution()
        self.curr_node = None
        self.ant_id = Ant.ant_id
        Ant.ant_id += 1

        self.portfolio = portfolio
        self.wrapper = wrapper
        

        self.graph = wrapper.get_graph()

        self.LEN = self.portfolio.model.duration

        self.unavailable = Set([])
        self.total_weight = 0
       

        self.capital = self.portfolio.model.budget


        self.generated = [0]* self.LEN
        self.substracted = [0] * self.LEN

        self.merged_glob = [self.capital] * self.LEN
        self.extra = []
        self.last_year = 0

        self.not_active = []
        self.drugs_so_far = {}
        self.position_to_year = [1]


        self.populate_inactive()
        self.move_next(wrapper.nest, {"complete": {}, "incomplete": []})
        
    
    def populate_inactive(self):
        for x in self.graph.nodes():
            node = self.graph.node[x]

            if node["active"] != True:
                self.not_active.append(x)


    def move_next(self, node, complete):
        self.unavailable.add(self.curr_node)
        self.update_curr_node(node)
        self.update_time(complete['complete'])


    def update_curr_node(self, node):
        self.curr_node = node
        self.solution.update_path(node)
        self.total_weight += self.graph.node[self.curr_node]['cost']
        self.enable_next_node(self.curr_node)

    def enable_next_node(self,node):
        if node is not "food" and node is not "nest":
            i = int(node[1:]) + 1
            next_node = str(node[0]) + str(i)

            if next_node in self.not_active:
                self.not_active.remove(next_node)

         

    def update_time(self, complete):
        
        #empty arrays for capital generated each year and spend each year
        generated_per_year = [0] * self.LEN
        spent_per_year = [0] * self.LEN

        #array for mapping the investment year with each stage
        diff = len(self.solution.path) - len(self.position_to_year)

        while(diff != 0):
            self.position_to_year.append(1)
            diff -= 1

        # based on completed drugs - calculate how much each generated per year and when
        for d, d_val in complete.iteritems():
            total_duration = 0
            for s, s_val in d_val.iteritems():
                total_duration += s_val["duration"]

            while total_duration < self.LEN:
                #print self.wrapper.profit_year
                generated_per_year[total_duration] += self.wrapper.profit_year[str(d)]
                total_duration += 1


        # eg. {u'B': 2, u'L': 4} and then {u'B': 5, u'L': 4}
        # keeps track on how much time passed since a drug started accounting for any gaps/break/wait in between too
        drugs_so_far = self.drugs_so_far

        # only for the last added stage to the solution as everything else is computed already
        last_added_stage = self.solution.path[-1]

        if last_added_stage is not "nest" and last_added_stage is not "food":
            drug = last_added_stage[:-1]

            if drug not in drugs_so_far.keys():
                drugs_so_far[drug] = 0

                      
            if drugs_so_far[drug] > self.last_year:
                wait = drugs_so_far[drug]
            else:
                wait = self.last_year


            # if total time exceeds portfolio time remove this from the solution path 
            # - to do : remove all last_added_stages related to this drug as drug not possible 
            if wait + self.graph.node[last_added_stage]["duration"] < self.LEN:
                self.position_to_year[-1] =  wait
                drugs_so_far[drug] = self.position_to_year[-1] + self.graph.node[last_added_stage]["duration"]
            else:
                self.solution.path.remove(last_added_stage)
                self.unavailable.add(last_added_stage)
                self.position_to_year.pop()

        
        #update the amount of money spend in each year
        for i in range(1, len(self.position_to_year)):
            stage = self.solution.path[i]
            position = self.position_to_year[i] - 1

            spent_per_year[position] -=  self.graph.node[stage]["cost"]

                
    

        merged = [0] * self.LEN
        self.substracted = [0] * self.LEN

        running_total = self.capital
        i = 0
        for x in range(0,self.LEN):
            merged[i] = running_total + spent_per_year[i] + generated_per_year[i]
            running_total = merged[i]

            self.substracted[i] = generated_per_year[i] + spent_per_year[i]
            i +=1

        self.merged_glob = merged
        self.generated = generated_per_year

            
        self.drugs_so_far = drugs_so_far


    def get_weight(self):
        return self.total_weight

    def get_neighbours(self):
        neigh = self.graph.neighbors(self.curr_node)
        sanitized = []

        next = True
        i = 1
        while next and i <= self.LEN:
            sanitized = []

            for x in neigh:
                if x not in self.solution.path and x not in self.unavailable and x not in self.not_active:
                    #TEST FOR EMPTY NODE{X} => node[x] = {}
                    cost = self.graph.node[x]["cost"]
                        
                    #check if current cost exceeds the available capital.
                    tmp_merged = self.merged_glob[i-1:]
                    tmp_merged = [a - cost for a in tmp_merged]
                    negative = sum(1 for n in tmp_merged if n < 0)
                    
                    if negative == 0 :
                        sanitized.append(x)

            # means for this year (year i) no stage was respecting the above constraint 
            # so we go to the next year where extra generated capital might be available
            if (len(sanitized) == 1 and "food" in sanitized):
                i+=1
            else:
                self.last_year = i
                self.extra = sanitized
                next = False

        return sanitized


