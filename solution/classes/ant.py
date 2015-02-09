from solution import Solution
from sets import Set
from time_window import TimeWindow


class Ant():

    ant_id = 0
    print_id = -1

    def __init__(self, wrapper, portfolio):
        self.solution = Solution()
        self.solution.ant = self
        self.curr_node = None
        self.ant_id = Ant.ant_id
        Ant.ant_id += 1

        self.G = wrapper.get_graph()

        self.p_duration = portfolio.model.duration
        self.capital = portfolio.model.budget

        self.unavailable = Set([])
        self.not_active = []
        self.total_weight = 0
        self.years = {}
        self.init_years();

        self.populate_inactive()

        self.so_far = {}

        self.last_enabled_node = None
        self.last_year = 2
        self.move_next(wrapper.nest, {"complete": {}, "incomplete": []})
        

       
    def get_so_far(self, node):
        print node
        drug_name = self.G.node[node]["drug"]["name"]

        if drug_name not in self.so_far:
            self.so_far[drug_name] = 0
            return 0
        else:
            return self.so_far[drug_name]

    def update_so_far(self, node, year):
        drug_name = self.G.node[node]["drug"]["name"]
        c= self.get_so_far(node)

        self.so_far[drug_name] += self.G.node[node]["duration"] + year - 1

    def init_years(self):
        for x in range(1,self.p_duration+1):
            self.years[x] = {"budget": self.capital, "items":[], "generated":0, "spent":0}   

    def populate_inactive(self):
        for x in self.G.nodes():
            node = self.G.node[x]

            if node["active"] != True:
                self.not_active.append(x)

    def move_next(self, node, complete):
        self.update_curr_node(node)
        self.solution.path.append(node)

    def update_curr_node(self, node):
        #previous node 
        self.unavailable.add(self.curr_node)
        #update it
        self.curr_node = node
        self.enable_next_node(self.curr_node)

        if node is "food" or node is "nest" or node is None:
            return
    
        #print node
        year = self.get_year(node)
        self.commit_year(year, node)
        
       
    def commit_year(self, year, node):
        if year > self.p_duration:
            print self.unavailable
            self.not_active.append(self.last_enabled_node)
            return

        entry = self.years[year]
        curr_budget = entry["budget"]
        node_cost = self.G.node[node]["cost"]
        generated = entry["generated"]
        spent = entry["spent"]

        if curr_budget + generated - node_cost + spent > 0:
            entry["items"].append(node)
        else:
            #no feasible solution here so close it
            self.curr_node = "food";
            self.solution.path.append("food")
            #print "AAAAAAAAAALSLALALALALALALALALALALALALALALALALALALDSALDLSALDALSDLASLDALSDAL"
            #x = 2/0

        self.update_so_far(node, year)

        #decrease available budget 
        for x in range(year, self.p_duration + 1):
            self.years[x]["spent"] -= node_cost


        if self.get_so_far(node) == self.G.node[node]["drug"]["total_duration"]:
            if self.get_so_far(node) < self.p_duration+1:
                for x in range(self.get_so_far(node)+1, self.p_duration+1):
                    self.years[x]["generated"] += self.G.node[node]["drug"]["profit_per_year"]
        """
        print node
        print self.so_far
        print "invested in year:" + str(year)
        print self.years
        print "------------------=========="
        """

    def get_year(self, node):
        year = self.get_so_far(node) + 1
        added = False
        
        #previous dependency constraint
       
        for x in range(year, self.p_duration):
            entry = self.years[x]
            tmp_budget = entry["budget"] + entry["generated"] - self.G.node[node]["cost"] + entry["spent"]
            
            #print "+++++++++++++++++++++++++++++"
            #print tmp_budget

            if tmp_budget > 0 and not added:
                year = x
                added = True

            if added and tmp_budget < 0:
                year = x + 1

        #print year
        #print self.so_far

        return year

        #print self.years
        #print self.so_far
        #print "----------------------"

    def check_dependency(self,items, node):
        pass
        #budget constraint


    

    def enable_next_node(self,node):
        if node is not "food" and node is not "nest":
            i = int(node[1:]) + 1
            next_node = str(node[0]) + str(i)

            if next_node in self.not_active:
                self.not_active.remove(next_node)
                self.last_enabled_node = next_node

        
    def get_neighbours(self):
        sanitized = [item for item in self.G.neighbors(self.curr_node) if item not in self.unavailable and item not in self.not_active]

        """  for x in sanitized:
                              if x is not "food"  and self.get_year(x) >= self.p_duration:
                                  sanitized.remove(x)"""
        return sanitized


