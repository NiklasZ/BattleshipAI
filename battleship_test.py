import unittest
import battleship_bot as bs

class TestDeployment(unittest.TestCase):

	#Check if it will reject invalid deployments.
	def test_deployment_reject(self):
		board = [['','2','2'],
		['','1',''],
		['','1','']]
		self.assertFalse(bs.canDeploy(0,0,board,2,'H'))
		self.assertFalse(bs.canDeploy(0,0,board,4,'V'))
		self.assertFalse(bs.canDeploy(1,1,board,1,'V'))
		self.assertFalse(bs.canDeploy(1,1,board,1,'H'))
		self.assertFalse(bs.canDeploy(2,2,board,2,'V'))
		self.assertFalse(bs.canDeploy(2,2,board,2,'H'))

if __name__ == '__main__':
    unittest.main()
