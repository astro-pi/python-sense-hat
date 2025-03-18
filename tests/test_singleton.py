from sense_hat import SenseHat
import unittest


class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        sense1 = SenseHat()
        sense2 = SenseHat()
        self.assertEqual(sense1.temperature, sense2.temperature)    

if __name__ == "__main__":
    unittest.main()