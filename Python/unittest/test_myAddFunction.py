from myCode import myAddFunction # This is the function we want to test
import unittest # The Python Unittest framework

class Test(unittest.TestCase): # Subclassing the TestCase class
  def test_sum_zeroes(self): # A test, that has to start with 'test_'
    self.assertEquals(myAddFunction(0,0), 0)
