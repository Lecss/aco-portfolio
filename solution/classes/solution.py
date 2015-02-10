

class Solution():

	def __init__(self):
		self.path = []
		self.value = 0
		self.years = {}
		self.ant = None
		self.time = 0
		
	def update_path(self, node):
		self.path.append(node)

