from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
import json

# VIEWS
class HomeCallsTest(TestCase):
	def test_call_get_portfolio_data(self):
		response = self.client.get(reverse("portfolio_data"))
		self.assertTrue(response.status_code == 200)
		response = json.loads(response.content)

		self.assertTrue("portfolio" in response.keys())
		self.assertTrue("drugs" in response["portfolio"])


	def test_call_get_graph(self):
		response = self.client.get(reverse("get_graph"), { "portfolio_id" : 1})
		self.assertTrue(response.status_code == 200)
		response = json.loads(response.content)

		self.assertTrue("directed" in response.keys())
		
