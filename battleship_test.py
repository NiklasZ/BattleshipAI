import unittest
import battleship_bot as bs
import numpy as np

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

	#Check if it will accept valid deployments
	def test_deployment_accept(self):
		board = [['','','',''],
		['','1','',''],
		['','1','','']]
		self.assertTrue(bs.canDeploy(0,0,board,2,'H'))
		self.assertTrue(bs.canDeploy(0,1,board,2,'H'))
		self.assertTrue(bs.canDeploy(0,0,board,4,'H'))
		self.assertTrue(bs.canDeploy(0,0,board,3,'V'))
		self.assertTrue(bs.canDeploy(0,2,board,3,'V'))
		self.assertTrue(bs.canDeploy(0,3,board,3,'V'))

class TestAlignments(unittest.TestCase):
	#Check if the method gets the right number of alignments given ships and board.
	def test_single_board_alignment(self):
		ships = [2,3]
		board = [['','','','',''],
		['','H','','',''],
		['L','','M','',''],
		['','M','','',''],
		['','M','','','']]
		self.assertEqual(bs.alignmentsIn(0,0,board,ships),3)
		self.assertEqual(bs.alignmentsIn(0,4,board,ships),4)
		self.assertEqual(bs.alignmentsIn(2,1,board,ships),0)

	#Check alignments on a whole board.
	def test_whole_board_alignment(self):
		ships = [2,3,4]
		board = [['','','',''],
		['','H','',''],
		['L','','M',''],
		['','M','','']]
		alignments_test = [[4,5,6,6],
		[1,0,2,6],
		[0,0,0,5],
		[0,0,1,4]]
		alignment_test_sum = 40

		alignments, alignment_sum  = bs.possibleAlignments(board,ships)
		for row, row_t in zip(alignments, alignments_test):
			for a, a_t in zip(row,row_t):
				self.assertEqual(a, a_t)
		self.assertEqual(alignment_sum, alignment_test_sum)

class TestTargeting(unittest.TestCase):

	def test_impact_targets(self):
		ships = [2,3]
		board = [['','',''],
		['','',''],
		['','','M']]
		alignments_test = [[4,5,3],
		[5,6,3],
		[3,3,0]]
		alignment_test_sum = 32

		#Test alignments again
		alignments, alignment_sum  = bs.possibleAlignments(board,ships)
		for row, row_t in zip(alignments, alignments_test):
			for a, a_t in zip(row,row_t):
				self.assertEqual(a, a_t)
		self.assertEqual(alignment_sum, alignment_test_sum)

		#Test some impact values
		impact_0_0 = bs.makeTarget(0,0,4,10) #If we shoot at (0,0)
		impact_0_1 = bs.makeTarget(0,1,5,12) #If we shoot at (0,1)
		impact_1_1 = bs.makeTarget(1,1,6,14) #If we shoot at (1,1)

		targets = bs.possibleTargets(board, ships)

		flag_0_0 = False
		flag_0_1 = False
		flag_1_1 = False
		
		for target in targets:
			if impact_0_0 == target:
				flag_0_0 = True
			if impact_0_1 == target:
				flag_0_1 = True
			if impact_1_1 == target:
				flag_1_1 = True

		self.assertTrue(flag_0_0)
		self.assertTrue(flag_0_1)
		self.assertTrue(flag_1_1)

if __name__ == '__main__':
    unittest.main()
