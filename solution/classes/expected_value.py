

class ExpectedValue():

	min_so_far = 0 

	def __init__(self, G, portfolio, path=None):
		self.G = G
		self.portfolio = portfolio
		self.years = {}
		self.path = path
		self.init_years()

		if path is not None:
			for stage in path:
				if stage is not "food" and stage is not "nest":
					self.add_to_year(stage)
		#print "----------000"
		#print self.portfolio.model.duration

	def init_years(self):
		years = {}
		for x in range(1, self.portfolio.model.duration+1):
			#print x
			self.years[x] = {"items":[], "restricted_items":[], "budget": self.portfolio.model.budget, "complete":[], "generated": 0}
		return years

	def compute(self, path):
		self.init_years()
		#path = ["nest","L1","L2","C1","J1","H1","I1","C2","I2","H2","G1", "H3","K1","K2", "K3","D1","D2","J2","A1","A2","D3", "J3","A3","G2","food" ] 
	
		self.path = path
		#print self.path
		
		#path = ['nest', u'C1', u'C2', u'L1', u'L2',u'I1', u'E1', u'I2', u'H1', u'H2',u'H3', u'E2', u'K1', u'K2', u'K3', u'E3', u'G1', u'G2', u'D1', u'A1', u'J1', u'A2', u'D2', u'A3', u'J2', u'J3', u'D3', 'food']
		#path = ["I1", "I2", "L1", "L2", "C1","C2", "H1", "H2", "H3"]
		#path = ["nest", "L1", "C1", "L2", "H1", "C2", "A1", "J1", "I1", "D1", "K1", "I2", "K2", "K3", 
		#"A2","H2", "E1","J2","H3","G1","D2","G2","D3","J3","A3","E2","E3"]
		for stage in path:
			if stage is "food" or stage is "nest":
				continue
			if not self.add_to_year(stage):
				return ExpectedValue.min_so_far

		#print self.years[10]["items"]
		#print path
		#self.print_trace()
		#print "============"

		expected_value = self.expected_value(path)

		if expected_value < ExpectedValue.min_so_far:
			min_so_far = expected_value

		return self.expected_value(path)

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

			for x in range(min_invest_year, self.portfolio.model.duration - stage_duration +1):
				if self.years[x]["budget"] -  stage_cost >= 0:
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


			if stage == self.G.node[stage]["last_stage"]:
				self.years[invested_in_year + stage_duration]["complete"].append(self.G.node[stage]["drug"]["name"])

				if (invested_in_year + stage_duration + 1) <= self.portfolio.model.duration:
					for x in range(invested_in_year + stage_duration +1, self.portfolio.model.duration+1):
						#print self.years[x]["generated"]
						diff = x - invested_in_year + stage_duration

						self.years[x]["generated"] = self.years[x]["generated"] \
												   + self.G.node[stage]["drug"]["profit_per_year"] * diff
						self.years[x]["budget"] = self.years[x]["budget"] \
												+ self.G.node[stage]["drug"]["profit_per_year"] * diff
						#print self.years[x]["generated"]

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

		for i in range(1, stages_count+1):
			if i is not stage_index:
				complements.append(drug_name + str(i))
		return complements

	def expected_value(self, path):
		"""cost = 0

		for x in self.years:
			for stage in self.years[x]["items"]:
				cost -= self.G.node[stage]["cost"] * self.G.node[stage]["arrive_here_prob"]

		complete_expected = 0
		
		for x in self.years:
			for d in  self.years[x]["complete"]:
				tmp_node = d + str(1)
				complete_expected += self.G.node[tmp_node]["drug"]["cummulated_prob"] * self.G.node[tmp_node]["drug"]["profit_per_year"] * (self.portfolio.model.duration - x)

		if complete_expected+cost > 74000:
			print path
		return complete_expected + cost
		"================================================" 
		"""
		cost = 0
		drugs_calculated = []
		
		#print path
		#path = ['nest', u'C1', u'L1', u'A1', u'L2', u'C2', u'H1', u'G1', u'A2', u'H2', u'H3', u'A3', u'I1', u'I2', u'G2', 'food']

		for x in self.path:
			#print x
			if x not in drugs_calculated and x is not "food" and x is not "nest":
				#print x
				drug = self.G.node[x]["drug"]["name"]
				stage_count = self.G.node[x]["drug"]["stages_count"]
				complement = self.get_stage_complement(x)
				all_stages = [x]
				drugs_calculated.append(x)
				drugs_calculated += complement
				all_stages+=complement
				"""
				print drug
				print all_stages
				print cost"""

				for i in all_stages:
					cost+= -1 * (stage_count+ 1 - self.G.node[i]["index"]) * self.G.node[i]["cost"] * self.G.node[i]["arrive_here_prob"]
					#print cost

		complete_expected = 0
		#print "=="
		for x in self.years:
			for d in  self.years[x]["complete"]:
				tmp_node = d + str(1)
				complete_expected += self.G.node[tmp_node]["drug"]["cummulated_prob"] * self.G.node[tmp_node]["drug"]["profit_per_year"] * (self.portfolio.model.duration - x)

		#print complete
		#print complete_expected+cost
		#print "=========="

		return complete_expected + cost
	def print_trace(self):
		generated = [self.years[x]["generated"] for x in self.years]
		print generated

		for x in self.years:
			print "\t" + str(x) + ": " + str(self.years[x]["items"]) + ": " + str(self.years[x]["budget"])# + str(self.years[x]["restricted_items"])
			print self.years[x]["complete"]







