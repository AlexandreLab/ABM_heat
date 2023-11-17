
import unittest
from heatingSystem import HeatingSystem
import pandas as pd
import numpy as np


class TestHeatingSystem(unittest.TestCase):


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
        fuel = "ngas"
        effHeat = 0.9 
        capex = 3000
        opex = 20
        lifespan = 15
        self.discountRate = 0.07
        self.annualHeatDemand = 10000
        self.fuelPrice = 0.02
        self.newHeatingSystem = HeatingSystem(heatingSystemName, dwellingType, fuel, effHeat, lifespan, capex, opex)
        return super().setUp()
    
    def tearDown(self) -> None:
        print('teardown')
        return super().tearDown()


    def test_calcNPV(self):
        print('test calcNPV')

    def test_calcEAC(self):
        print('test calcEAC')
        #self.capex*discountRate/(1-np.power((1+discountRate),-self.lifespan))+self.calcTotalOPEX(annualHeatDemand, fuelPrice)
        totalOPEX = self.annualHeatDemand/0.9*0.02+20
        EAC = 3000*self.discountRate/(1-np.power((1+self.discountRate),-15))+totalOPEX
        self.assertEqual(self.newHeatingSystem.calcEAC(self.annualHeatDemand, self.fuelPrice, self.discountRate), EAC)

    def test_calcCAPEX(self):
        print('test calcCAPEX')
        self.assertEqual(self.newHeatingSystem.calcCAPEX(), 3000)
        

        
        

if __name__ == '__main__':
    unittest.main()

