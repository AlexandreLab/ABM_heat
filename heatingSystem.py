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
        # self.lowCarbonFlag = False
 
    # ADD @property getter and setter for the properties
    # 

    def calcCost(self, method, annualHeatDemand, fuelPrice, discountRate, timeHorizon, currentYear):
        cost = 0
        if method == "CAPEX":
            cost = self.calcCAPEX(discountRate, currentYear)
        elif method == "EAC":
            cost = self.calcEAC(annualHeatDemand, fuelPrice, discountRate, currentYear)
        elif method == "NPV":
            cost = self.calcNPV(annualHeatDemand, fuelPrice, discountRate, timeHorizon, currentYear)
        else: print('Method {0} is not recognised'.format(method))
        return cost

    def calcCurrentYearCost(self, value, discountRate, currentYear):
        return value *np.power(1+discountRate,-currentYear)

    def calcCAPEX(self, discountRate, currentYear):
        #print('CAPEX')
        return self.calcCurrentYearCost(self.capex, discountRate, currentYear)

    def calcEAC(self, annualHeatDemand, fuelPrice, discountRate, currentYear):
        #print('EAC')
        capex = self.calcCAPEX(discountRate, currentYear)
        return capex*discountRate/(1-np.power((1+discountRate),-self.lifespan))+self.calcTotalOPEX(annualHeatDemand, fuelPrice, discountRate, currentYear)

    def calcNPV(self, annualHeatDemand, fuelPrice, discountRate, timeHorizon, currentYear):
        timespan = self.lifespan
        NPV = 0
        capex = self.calcCAPEX(discountRate, currentYear)
        opex = self.calcTotalOPEX(annualHeatDemand, fuelPrice, discountRate, currentYear)
        if timeHorizon>0:
            if timeHorizon > timespan:
                raise ValueError('TimeHorizon of {0} is longer than the lifespan {1} of the heating system'.format(timeHorizon, self.lifespan))
            else: 
                timespan = timeHorizon
        
        if timespan<self.lifespan: #only include the OPEX of the heating system for the time horizon
            NPV = opex*(1-np.power((1+discountRate),-timespan))/discountRate
        else:
            NPV = capex + opex*(1-np.power((1+discountRate),-self.lifespan))/discountRate
        return NPV

    def calcTotalOPEX(self, annualHeatDemand, fuelPrice, discountRate, currentYear):
        opex = self.calcCurrentYearCost(self.opex + annualHeatDemand / self.efficiencyHeat * fuelPrice, discountRate, currentYear)   
        return opex


    @property
    def lifespan(self):
        return self._lifespan

    @lifespan.setter
    def lifespan(self, value):
        # print('Setting new annual heat demand')
        if isinstance(value, float):
            value = int(round(value, 0))

        if not isinstance(value, int):
            raise TypeError('Expected a integer')
        if value < 0:
            raise ValueError('lifespan less than 0 is not possible')
        self._lifespan = value