from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import unittest
import time


class NewVisitorTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()
# Put helper methods near top class, btwn teardown and first test
    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_for_one_user(self):
        # Claires heard of a new to-do web app. She goes to the site
        # to check it out.
        self.browser.get(self.server_url)

        # She notices the page title and header mention the To-Do list
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # She's prompted to enter a to-do item and test the app herself
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # She types in "Look for a post-office" into a text box
        inputbox.send_keys('Look for a post-office')

        # She hits enter, and upon doing so, the page updates and now
        # lists: "1: Look for a post-office"
        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('1: Look for a post-office')


        # The text-box remains for her to input another item. She enters:
        # "Ask Kris to send over go-pro"
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Ask Kris to send over go-pro')
        inputbox.send_keys(Keys.ENTER)


        # The page updates a second time and both her items are still
        # on the list
        self.check_for_row_in_list_table('2: Ask Kris to send over go-pro')
        self.check_for_row_in_list_table('1: Look for a post-office')


    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Claire starts a new todo list
        self.browser.get(self.server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Look for a post-office')


        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('1: Look for a post-office')

        # She notices that her list has a unique URL
        claire_list_url = self.browser.current_url
        self.assertRegex(claire_list_url, '/lists/.+')

        # Now a new user, Francis, comes along to the site.

        ## We use a new browser session to make sure that no information
        ## of Claire's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Francis visits the home page.  There is no sign of Claire's
        # list
        self.browser.get(self.server_url)

        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Look for a post-office', page_text)
        self.assertNotIn('to send over', page_text)

        # Francis starts a new list by entering a new item. He
        # is less interesting than Edith...
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('1: Buy milk')
        # Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, claire_list_url)

        # Again, there is no trace of Claire's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Look for a post-office', page_text)
        self.assertIn('Buy milk', page_text)

        # Satisfied, they both go back to sleep

    def test_layout_and_styling(self):
        # Claire goes to the home page
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=5
        )
        # She starts a new list and sees the input is nicely
        # centered there too
        inputbox.send_keys('testing\n')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=5
        )