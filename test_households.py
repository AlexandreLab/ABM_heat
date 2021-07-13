
import unittest
from households import Households
import pandas as pd


class TestHouseholds(unittest.TestCase):


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
        self.housholdsGroup1 = Households(1)
        self.dfDwellingCategories = pd.DataFrame(columns = ["DwellingType", "HeatingSystem", "NumberOfUnits"])
        self.dfDwellingCategories["DwellingType"] = ["Detached house"]
        self.dfDwellingCategories["HeatingSystem"] = ["Gas boiler"]
        self.dfDwellingCategories["NumberOfUnits"] = [3]
        return super().setUp()
    
    def tearDown(self) -> None:
        print('teardown')
        return super().tearDown()


    def test_addDwellingCategories(self):
        print('test importDwellingCategories')
        
        # test raiseValue for dwelling type
        self.dfDwellingCategories["DwellingType"] = ["Detached"]

        with self.assertRaises(ValueError):
            self.housholdsGroup1.importDwellingCategories(self.dfDwellingCategories)

        # test raiseValue for heating system
        self.dfDwellingCategories["HeatingSystem"] = ["Unknownheatingsystem"] #### wrong heating system value

        with self.assertRaises(ValueError):
            self.housholdsGroup1.importDwellingCategories(self.dfDwellingCategories)

        # test raiseValue for numberofUnit
        self.dfDwellingCategories["NumberOfUnits"] = [-10000] #### wrong number of untis value

        with self.assertRaises(ValueError):
            self.housholdsGroup1.importDwellingCategories(self.dfDwellingCategories)

    def test_calcHeatDemandByHeatingSystem(self):
        print('test calcHeatDemandByHeatingSystem')
        self.housholdsGroup1.importDwellingCategories(self.dfDwellingCategories)

        # Test that the keys and values of the dict returned
        self.assertSetEqual(set(map(type, self.housholdsGroup1.calcHeatDemandByHeatingSystem.values())), {int})
        self.assertIn("Gas boiler", self.housholdsGroup1.calcHeatDemandByHeatingSystem)
        self.assertEqual(self.housholdsGroup1.calcHeatDemandByHeatingSystem["Gas boiler"], 45000)
        
        

if __name__ == '__main__':
    unittest.main()

