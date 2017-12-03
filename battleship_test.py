import unittest
import battleship_bot as bs

class TestDeployment(unittest.TestCase):

	def test_reject(self):
		board = [['','2','2'],
		['','1',''],
		['','1','']]
		assert(bs.canDeploy(0,0))