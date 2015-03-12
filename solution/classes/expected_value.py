import copy
from sets import Set


class ExpectedValue():
    min_so_far = 0
    cost_per_drug = {}
    paths_computed = {}

    def __init__(self, G, portfolio, path=[], failed=[]):
        self.G = G
        self.portfolio = portfolio
        self.years = {}
        self.path = path
        self.set_path = Set()
        self.init_years()
        self.failed_drugs = [self.G.node[x]["drug"]["name"] for x in failed]

        for stage in path:
            if stage is not "food" and stage is not "nest":
                self.add_to_year(stage)


    def init_years(self):
        years = {}
        for x in range(1, self.portfolio.model.duration + 1):
            self.years[x] = {"items": [], "restricted_items": [], "budget": self.portfolio.model.budget, "complete": [],
                             "generated": 0}
        return years

    def compute(self, path, failed=[]):
        self.init_years()

        # if str(path) in ExpectedValue.paths_computed.keys():
        #return ExpectedValue.paths_computed[str(path)]

        self.failed_drugs = [self.G.node[x]["drug"]["name"] for x in failed]
        self.path = path
        self.set_path = Set() if len(path) == 0 else Set(path)

        for stage in path:
            if stage is "food" or stage is "nest":
                continue
            if not self.add_to_year(stage):
                return None

        #calculate the expected value
        expected_value = self.expected_value()

        #update the minimum found so far
        if expected_value < ExpectedValue.min_so_far:
            min_so_far = expected_value

        ExpectedValue.paths_computed[str(path)] = expected_value

        return expected_value

    def add_to_year(self, stage, year_needed=False):
        complement = self.get_stage_complement(stage)
        stage_cost = self.G.node[stage]["cost"]
        stage_duration = self.G.node[stage]["duration"]

        min_invest_year = 1

        for x in self.years:
            if self.years[x]["budget"] - stage_cost < 0 or stage in self.years[x]['restricted_items']:
                min_invest_year = x + 1

        can_add = self.portfolio.model.duration - min_invest_year > stage_duration

        if can_add:
            invested_in_year = min_invest_year

            for x in range(min_invest_year, self.portfolio.model.duration - stage_duration + 1):
                if self.years[x]["budget"] - stage_cost >= 0:
                    if stage not in self.years[x]["restricted_items"]:
                        self.years[x]["items"].append(stage)
                        invested_in_year = x
                        break

            if year_needed:
                return invested_in_year

            for x in range(invested_in_year, self.portfolio.model.duration + 1):
                self.years[x]["budget"] = self.years[x]["budget"] - stage_cost

            for x in range(1, invested_in_year + stage_duration):
                self.years[x]["restricted_items"] += complement

            if stage == self.G.node[stage]["last_stage"] and self.G.node[stage]["drug"][
                "name"] not in self.failed_drugs:
                self.years[invested_in_year + stage_duration]["complete"].append(self.G.node[stage]["drug"]["name"])

                if (invested_in_year + stage_duration + 1) <= self.portfolio.model.duration:
                    for x in range(invested_in_year + stage_duration + 1, self.portfolio.model.duration + 1):
                        # print self.years[x]["generated"]
                        diff = x - invested_in_year + stage_duration

                        self.years[x]["generated"] = self.years[x]["generated"] \
                                                     + self.G.node[stage]["drug"]["profit_per_year"] * diff
                        self.years[x]["budget"] = self.years[x]["budget"] \
                                                  + self.G.node[stage]["drug"]["profit_per_year"] * diff

            return True
        else:
            return False

    def years_(self):
        return self.years

    def get_stage_complement(self, node):
        if node is "food" or node is "nest":
            return []

        stages_count = self.G.node[node]["drug"]["stages_count"]
        stage_index = self.G.node[node]["index"] + 1
        drug_name = self.G.node[node]["drug"]["name"]
        complements = []

        for i in range(1, stages_count + 1):
            if i is not stage_index:
                complements.append(drug_name + str(i))
        return complements

    def expected_value(self):
        cost = self.get_fixed_cost()
        complete_expected = 0

        # compute the generated value across the years
        for x in self.years:
            for d in self.years[x]["complete"]:
                tmp_node = d + str(1)
                drug = self.G.node[tmp_node]["drug"]
                complete_expected += drug["cummulated_prob"] * drug["profit_per_year"] * (
                    self.portfolio.model.duration - x)

        return complete_expected + cost

    def get_fixed_cost(self):
        drugs_calculated = []
        cost = 0
        path = self.path

        for i in self.path:
            stage_count = self.G.node[i]["drug"]["stages_count"]
            cost += self.G.node[i]["cost"] * self.G.node[i]["arrive_here_prob"]


            # get the fixed cost for every drug
        """for x in self.path:
			if x not in drugs_calculated and x is not "food" and x is not "nest":
				drug = self.G.node[x]["drug"]["name"]
				complement = self.get_stage_complement(x)
				drugs_calculated.append(x)
				drugs_calculated += complement

				if drug in ExpectedValue.cost_per_drug.keys():
					cost+= ExpectedValue.cost_per_drug[drug]
				else:
					stage_count = self.G.node[x]["drug"]["stages_count"]
					all_stages = [x]
					all_stages +=complement

					drug_cost = 0
					for i in all_stages:
						drug_cost += -1 * (stage_count+ 1 - self.G.node[i]["index"]) * self.G.node[i]["cost"] * self.G.node[i]["arrive_here_prob"]
					
					ExpectedValue.cost_per_drug[drug] = drug_cost
					cost += drug_cost

		diff = Set(drugs_calculated) - self.set_path
		for i in diff:
			stage_count = self.G.node[i]["drug"]["stages_count"]
			cost -= (stage_count+ 1 - self.G.node[i]["index"]) * self.G.node[i]["cost"] * self.G.node[i]["arrive_here_prob"]
    """
        return cost

def print_trace(self):
    generated = [self.years[x]["generated"] for x in self.years]
    print generated

    for x in self.years:
        print "\t" + str(x) + ": " + str(self.years[x]["items"]) + ": " + str(
            self.years[x]["budget"])  # + str(self.years[x]["restricted_items"])
        print self.years[x]["complete"]







