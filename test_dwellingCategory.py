
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
        
        self.fuelPrices = {"electricity": 0.15, "ngas":0.04}

        newHeatingSystem = HeatingSystem(heatingSystemName, dwellingType, "ngas", 0.9, 15, 3000, 50)
        numberOfUnit = 100
        #dwellingType, heatingSystem, numberOfUnit,currentEPC, potentialEPC, currentHeatDemand, potentialHeatDemand, costEEImprovements, currentYear
        self.newDwelling = DwellingCategory(dwellingType, newHeatingSystem, numberOfUnit, 60, 75, 15000, 10000, 5000, 0)
        return super().setUp()
    
    def tearDown(self) -> None:
        print('teardown')
        return super().tearDown()


    def test_annualHeatDemand(self):
        

        with self.assertRaises(ValueError):
            self.newDwelling.currentAvgAnnualHeatDemand = -1000
        
        with self.assertRaises(TypeError):
            self.newDwelling.currentAvgAnnualHeatDemand = "test"


    # Verify the NPV calculations
    def test_calcNPVEnergyEfficiency(self):
        # calcNPVEnergyEfficiency(capex, opex, discountRate, lifespan)
        self.assertEqual(round(self.newDwelling.calcNPVEnergyEfficiency(0, 100, 0.07, 6), 0), 577)
        self.assertEqual(round(self.newDwelling.calcNPVEnergyEfficiency(1500, 100, 0.07, 6), 0), -923)

        
        

if __name__ == '__main__':
    unittest.main()

