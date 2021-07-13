import numpy as np


class HeatingSystem():

    def __init__(self, name, targetDwelling, fuel, efficiencyHeat, lifetime, capex, opex):
        self.fuel = fuel
        self.name = name
        self.targetDwelling = targetDwelling
        self.efficiencyHeat = efficiencyHeat
        self.capex = capex
        self.opex = opex #opex excluding fuel cost
        self.lifetime = lifetime

    # ADD @property getter and setter for the properties
    # 

    def calcCost(self, method, annualHeatDemand, fuelPrice, discountRate):
        cost = 0
        if method == "CAPEX":
            cost = self.calcCAPEX()
        elif method == "EAC":
            cost = self.calcEAC(annualHeatDemand, fuelPrice, discountRate)
        elif method == "NPV":
            cost = self.calcNPV()
        else: print('Method {0} is not recognised'.format(method))
        return cost

    def calcCAPEX(self):
        #print('CAPEX')
        return self.capex

    def calcEAC(self, annualHeatDemand, fuelPrice, discountRate):
        #print('EAC')
        return self.capex*discountRate/(1-np.power((1+discountRate),-self.lifetime))+self.calcTotalOPEX(annualHeatDemand, fuelPrice)

    def calcNPV(self):
        #print('NPV')
        return 0


    def calcTotalOPEX(self, annualHeatDemand, fuelPrice):
        return self.opex+ annualHeatDemand/self.efficiencyHeat*fuelPrice