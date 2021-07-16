

from heatingSystem import HeatingSystem

class DwellingCategory():

    def __init__(self,dwellingType, heatingSystem, numberOfUnit):
        self.avgCumulativeCost = 0
        
        self.numberOfUnit = numberOfUnit
        self.ownership = "basic"
        self.dwellingType = dwellingType
        self.heating = ""
        self.heatingSystem = heatingSystem
        self.previousHeatingSystem = None
        self.energyEfficiencyLevel = "EPC_C"
        self.avgAnnualHeatDemand = 15000 # average annual heat demand for this dwelling category
        self.heatingSystemTurnOver = 0.3*numberOfUnit # amount of dwellingas that can switch to a different heating systems every year.
        print("New dwelling category was created: {0} with {1}".format(dwellingType, heatingSystem.name))
        self.currentOPEX = 0


    @property
    def heatingSystemTurnOver(self):
        return self._heatingSystemTurnOver

    @heatingSystemTurnOver.setter
    def heatingSystemTurnOver(self, value):
        self._heatingSystemTurnOver = value

    @property
    def numberOfUnit(self):
        return self._numberOfUnit

    @numberOfUnit.setter
    def numberOfUnit(self, value):
        self._numberOfUnit = value
        

    def updateCumulativeCost(self):
        self.avgCumulativeCost = self.avgCumulativeCost + self.heatingSystem.capex  #Add capex of the new heating system to the cumulative cost

    def incrementCumulativeCost(self):
        self.avgCumulativeCost = self.avgCumulativeCost + self.currentOPEX

    @property
    def currentOPEX(self):
        return self._currentOPEX

    @currentOPEX.setter
    def currentOPEX(self, value):
        self._currentOPEX = value

    def calcCurrentOPEX(self, fuelPrices):
        fuel = self.heatingSystem.fuel
        fuelPrice = fuelPrices[fuel]
        value = self.heatingSystem.calcTotalOPEX(self.avgAnnualHeatDemand, fuelPrice)
        self.currentOPEX = value

    def getCheapestNewHeatingSystem(self, dictHeatingSystems,discountRate, fuelPrices, timeHorizon, method):
        fuel = self.heatingSystem.fuel
        fuelPrice = fuelPrices[fuel]
        minCost = self.heatingSystem.calcCost(method, self.avgAnnualHeatDemand, fuelPrice, discountRate, timeHorizon)
        
        print('The {0} of the dwelling with the current heating system ({1}) is: £{2:,.0f}'.format(method ,self.heatingSystem.name, minCost ))

        keyCheaperHeatingSystem = -1
        for k, v in dictHeatingSystems.items():
            if v.targetDwelling == self.dwellingType and v.name != self.heatingSystem.name:
                fuel = v.fuel
                fuelPrice = fuelPrices[fuel]
                tempCost = v.calcCost(method, self.avgAnnualHeatDemand, fuelPrice, discountRate, timeHorizon)
                if tempCost<minCost:
                    keyCheaperHeatingSystem = k
                    minCost = tempCost
                print('The {0} of the dwelling with a new {1} is: £{2:,.0f}'.format(method, v.name, tempCost))

        return keyCheaperHeatingSystem


    @property
    def heatingSystem(self):
        #print('Return current heating system')
        return self._heatingSystem


    @heatingSystem.setter
    def heatingSystem(self, value):
        if not isinstance(value, HeatingSystem):
            raise TypeError('Expected a HeatingSystem object')
        print('Setting new heating system: {0}'.format(value.name))
        self._heatingSystem = value


    @property
    def previousHeatingSystem(self):
        #print('Return current heating system')
        return self._previousHeatingSystem


    @previousHeatingSystem.setter
    def previousHeatingSystem(self, value):
        self._previousHeatingSystem = value

    @property
    def avgAnnualHeatDemand(self):
        return self._annualHeatDemand

    @avgAnnualHeatDemand.setter
    def avgAnnualHeatDemand(self, value):
        print('Setting new annual heat demand')
        if not isinstance(value, int):
            raise TypeError('Expected a integer')
        if value < 0:
            raise ValueError('avgAnnualHeatDemand less than 0 is not possible')
        self._annualHeatDemand = value


    def totalAnnualHeatDemand(self):
        return self.avgAnnualHeatDemand * self.numberOfUnit



if __name__ == '__main__':
    heating1 = HeatingSystem("Gas boiler", "Detached house", "ngas", 0.9, 15, 3000, 0)
    dwelling1 = DwellingCategory("Detached house", heating1, 30)

    print(dwelling1.heatingSystem.name)
    

    heating2 = HeatingSystem("ASHP", "Detached house", "electricity", 2.5, 20, 15000, 0)
    dwelling1.heatingSystem = heating2
    print(dwelling1.heatingSystem.name)

    dwelling1.avgAnnualHeatDemand = 100
    print(dwelling1.avgAnnualHeatDemand)