from sense_hat import SenseHat
import unittest
import time
import concurrent.futures


def get_temp(dummy):
    sense = SenseHat()
    time.sleep(5)
    print(dummy)
    return round(sense.get_temperature())

class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        sense1 = SenseHat()
        sense2 = SenseHat()
        self.assertEqual(sense1.get_temperature(), sense2.get_temperature())    
        self.assertEqual(sense1, sense2)
        
    @unittest.expectedFailure   
    def test_multiprocess(self):
        executions = ["run1", "run2", "run3", "run4", "run5"]
        prev_temp = None
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for temp in executor.map(get_temp,executions):
                if prev_temp:
                    print(prev_temp, temp)
                    self.assertEqual(temp, prev_temp)
                prev_temp = temp    
                
                
if __name__ == "__main__":
    unittest.main()