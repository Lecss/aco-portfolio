
# Create your tests here.
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from django.test import LiveServerTestCase

from django.core.urlresolvers import reverse

class HomeTest(LiveServerTestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
    """
    def tearDown(self):
        self.browser.quit()

    def test_can_see_home_page(self):
        # User opens web browser, and goes to the home page
        self.browser.get(self.live_server_url)
        
        body = self.browser.find_element_by_tag_name("body")

        # Can now see the portfolio displayed
        self.assertIn("Leopard", body.text)
        self.assertIn("ACO Portfolio", self.browser.title)
  
    def test_can_submit_and_see_result(self):
        self.browser.get(self.live_server_url)

        form = self.browser.find_element_by_id("drug_form")
        form.submit()

        body = self.browser.find_element_by_tag_name("body")

        self.assertIn("Results page", self.browser.title)
        self.assertIn("directed", body.text)
    """