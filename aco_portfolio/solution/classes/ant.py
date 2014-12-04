from solution import Solution
from sets import Set
from time_window import TimeWindow


class Ant():

    ant_id = 0
    print_id = -1

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
        self.generated = [0]*11
        self.substracted = [0] * 11

        self.merged_glob = [self.capital] * 11
        self.extra = []
        self.last_year = 0

        self.not_active = []
        self.drugs_so_far = {}
        self.position_to_year = [0]


        self.populate_inactive()
        self.move_next(wrapper.nest, {"complete": {}, "incomplete": []})
        
    
    def populate_inactive(self):

        for x in self.graph.nodes():

            node = self.graph.node[x]

            if node["active"] != True:
                self.not_active.append(x)




    def move_next(self, node, complete):
        self.unavailable.add(self.curr_node)
        self.solution.update_path(node)
        self.curr_node = node
        self.total_weight += self.graph.node[self.curr_node]['cost']

        self.make_active(self.curr_node)
        #print complete
        self.update_time(complete['complete'])

    def make_active(self,node):
        
        if node is not "food" and node is not "nest":
            i = int(node[1:]) + 1

            next_node = str(node[0]) + str(i)

            if next_node in self.not_active:
                self.not_active.remove(next_node)

         

    def update_time(self, complete):
        tmp_capital = self.capital 
        generated_per_year = [0] * 11
        spent_per_year = [0] * 11


        diff = len(self.solution.path) - len(self.position_to_year)

        while(diff != 0):
            self.position_to_year.append(0)
            diff -= 1

        for d, d_val in complete.iteritems():
            total_duration = 1
            for s, s_val in d_val.iteritems():
                total_duration += s_val["duration"]

            while total_duration < 11:
                #print self.wrapper.profit_year
                generated_per_year[total_duration] += self.wrapper.profit_year[str(d)]
                total_duration += 1

        drugs_so_far = self.drugs_so_far

        i = len(self.solution.path)-1
        stage = self.solution.path[i]

        if stage is not "nest" and stage is not "food":
            drug = stage[:-1]

            if drug not in drugs_so_far.keys():
                drugs_so_far[drug] = 0

            wait = 0

            if stage in self.extra:            
                if drugs_so_far[drug] > self.last_year:
                    wait = drugs_so_far[drug]
                else:
                    wait = self.last_year


            # if total time exceeds portfolio time remove this from the solution path 
            # - to do : remove all stages related to this drug as drug not possible 
            if wait + self.graph.node[stage]["duration"]< 11:
                self.position_to_year[i] =  wait
                drugs_so_far[drug] = self.position_to_year[i] + self.graph.node[stage]["duration"]
            else:
                self.solution.path.remove(stage)
                self.unavailable.add(stage)
                self.position_to_year.pop()

        i =0
        for y in self.position_to_year:
            try:
                stage = self.solution.path[i]
                spent_per_year[y] -= self.graph.node[stage]["cost"]
                i+=1
            except:
                pass
        if self.ant_id == 20222:
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

        self.merged_glob = merged
        self.generated = generated_per_year


        if sum(generated_per_year) != 0 and Ant.print_id == -1:
            pass
            #Ant.print_id = self.ant_id
            
        self.drugs_so_far = drugs_so_far


    def get_weight(self):
        return self.total_weight

    def get_neighbours(self):
        neigh = self.graph.neighbors(self.curr_node)
        sanitized = []

        if self.substracted[0] * -1 > self.capital + 3000:
            raw_input("Enter your name: " + str(Ant.print_id))


        next = True
        i = 0 
        while next and i < 10:
            sanitized = []

            for x in neigh:
                if x not in self.solution.path and x not in self.unavailable and x not in self.not_active:
                    #TEST FOR EMPTY NODE{X} => node[x] = {}
                    cost = self.graph.node[x]["cost"]


                    """if self.ant_id == Ant.print_id:
                                                                                    print "-------------------------------------------------------------------------------------"
                                                                                    print "Cost: \t" + str(cost)
                                                                                    print "Path: \t" + str(self.solution.path)
                                                                                    print "Position: \t" + str(self.position_to_year)
                                                                                    print "Substracted: \t" + str(self.substracted)
                                                                                    print "Generated: \t" + str(self.generated)
                                                                                    print 
                                                                                    print "Merged: \t" + str(self.merged_glob)
                                                            
                                                                                    print "I ("+ str(i) +"): " """
                        
                    tmp_merged = self.merged_glob[i:]

                    """if self.ant_id == Ant.print_id: 
                                                                                    print "tmp_merged trimmed: \t" + str(tmp_merged)"""

                    tmp_merged = [a - cost for a in tmp_merged]
                    """if self.ant_id == Ant.print_id: 
                                                                                    print "tmp_merged - cost: \t" + str(tmp_merged)
                                                                                    print "Merged again: \t" + str(self.merged_glob)"""

                    negative = sum(1 for n in tmp_merged if n < 0)

                    
                    if negative == 0 :
                        sanitized.append(x)


            if (len(sanitized) == 0 or (len(sanitized) == 1 and "food" in sanitized)):
                i+=1
            else:
                self.last_year = i
                self.extra = sanitized
                next = False

        return sanitized


