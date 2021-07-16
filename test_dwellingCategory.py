
import unittest
from dwellingCategory import DwellingCategory
from heatingSystem import HeatingSystem
import pandas as pd


class TestDwellingCategory(unittest.TestCase):


    @classmethod
    def setUpClass(cls) -> None:
        print('setupClass')

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        print('teardownClass')
        return super().tearDownClass()

    def setUp(self) -> None:
        print('setup')
        dwellingType = "Detached house"
        heatingSystemName = "Gas boiler"
        newHeatingSystem = HeatingSystem(heatingSystemName, dwellingType, "ngas", 0.9, 15, 3000, 0)
        numberOfUnit = 100
        self.newDwelling = DwellingCategory(dwellingType, newHeatingSystem, numberOfUnit)
        return super().setUp()
    
    def tearDown(self) -> None:
        print('teardown')
        return super().tearDown()


    def test_annualHeatDemand(self):
        

        with self.assertRaises(ValueError):
            self.newDwelling.annualHeatDemand = -1000
        
        with self.assertRaises(TypeError):
            self.newDwelling.annualHeatDemand = "test"


if __name__ == '__main__':
    unittest.main()

