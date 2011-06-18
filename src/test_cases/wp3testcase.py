'''
Created on Jun 18, 2011

@author: fabio
'''

from simulation import test_case
import re

class Wp3TestCase(test_case.TestCase):
    
    def setUp(self):
        self.simulator.load('http://wptesi/wp_3-1-3/wp-admin')
        if re.search(r"wp-login", self.simulator.current_url): 
            self.simulator.fill('#loginform :text', 'admin')
            self.simulator.fill('#loginform :password', 'cactus')
            self.simulator.click('#loginform :submit')
        
    def testWritePost(self):
        self.simulator.clickLinkMatching(r"add new", '#menu-posts a')
        self.simulator.assertPageTitle(r"add new post")
        
        self.simulator.sendText('input[name=post_title]', 'Dummy post title')
        
        self.simulator.click('#edButtonHTML', False);
        self.simulator.fill('#content', 'Some dummy content', assert_visible=False)
        self.simulator.click('#publish');
        self.simulator.assertPageTitle(r"edit post")
        self.simulator.assertTextMatch('post published', '#message')
        
        self.simulator.assertInputValue('Dummy post title', 'input[name=post_title]')
        
        self.simulator.clickLinkMatching(r"posts", '#menu-posts a')
        self.simulator.assertPageTitle(r"posts")
        self.simulator.click('#date a')
        self.simulator.assertTextMatch('dummy post title', 'table.posts .post-title')
        
        
    def testTrashPost(self):
        self.simulator.clickLinkMatching(r"posts", '#menu-posts a')
        self.simulator.clickNearestTo(':checkbox', ':contains("Dummy post title")', 'tr', False)
        self.simulator.select('select[name=action]', 'trash')
        self.simulator.click('#doaction')
        self.simulator.assertTextMatch('Item moved to the Trash', '#message')
        
