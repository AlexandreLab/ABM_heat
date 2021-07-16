import numpy as np


class HeatingSystem():

    def __init__(self, name, targetDwelling, fuel, efficiencyHeat, lifespan, capex, opex):
        self.fuel = fuel
        self.name = name
        self.targetDwelling = targetDwelling
        self.efficiencyHeat = efficiencyHeat
        self.capex = capex
        self.opex = opex #opex excluding fuel cost
        self.lifespan = lifespan
 
    # ADD @property getter and setter for the properties
    # 

    def calcCost(self, method, annualHeatDemand, fuelPrice, discountRate, timeHorizon):
        cost = 0
        if method == "CAPEX":
            cost = self.calcCAPEX()
        elif method == "EAC":
            cost = self.calcEAC(annualHeatDemand, fuelPrice, discountRate)
        elif method == "NPV":
            cost = self.calcNPV(annualHeatDemand, fuelPrice, discountRate, timeHorizon)
        else: print('Method {0} is not recognised'.format(method))
        return cost

    def calcCAPEX(self):
        #print('CAPEX')
        return self.capex

    def calcEAC(self, annualHeatDemand, fuelPrice, discountRate):
        #print('EAC')
        return self.capex*discountRate/(1-np.power((1+discountRate),-self.lifespan))+self.calcTotalOPEX(annualHeatDemand, fuelPrice)

    def calcNPV(self, annualHeatDemand, fuelPrice, discountRate, timeHorizon):
        timespan = self.lifespan
        NPV = 0
        if timeHorizon>0:
            if timeHorizon > timespan:
                raise ValueError('TimeHorizon of {0} is longer than the lifespan {1} of the heating system'.format(timeHorizon, self.lifespan))
            else: 
                timespan = timeHorizon
        
        if timespan<self.lifespan: #only include the OPEX of the heating system for the time horizon
            NPV = self.calcTotalOPEX(annualHeatDemand, fuelPrice)*(1-np.power((1+discountRate),-timespan))/discountRate
        else:
            NPV = self.capex + self.calcTotalOPEX(annualHeatDemand, fuelPrice)*(1-np.power((1+discountRate),-self.lifespan))/discountRate
        return NPV


    def calcTotalOPEX(self, annualHeatDemand, fuelPrice):
        return self.opex + annualHeatDemand / self.efficiencyHeat * fuelPrice