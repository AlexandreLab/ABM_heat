

from heatingSystem import HeatingSystem


class DwellingCategory():
    

    def __init__(self,dwellingType, heatingSystem, numberOfUnit):
        self.list_households =[]
        self.cumulativeCosts = 0
        self.numberOfUnit = numberOfUnit
        self.ownership = "basic"
        self.dwellingType = dwellingType
        self.heating = ""
        self.heatingSystem = heatingSystem
        self.energyEfficiencyLevel = "EPC_C"
        self.annualHeatDemand = 15000 # average annual heat demand for this dwelling category
        print("New dwelling category was created: {0} with {1}".format(dwellingType, heatingSystem.name))

        
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
    def annualHeatDemand(self):
        return self._annualHeatDemand

    @annualHeatDemand.setter
    def annualHeatDemand(self, value):
        print('Setting new annual heat demand')
        if not isinstance(value, int):
            raise TypeError('Expected a integer')
        if value < 0:
            raise ValueError('annualHeatDemand less than 0 is not possible')
        self._annualHeatDemand = value


if __name__ == '__main__':
    heating1 = HeatingSystem("Gas boiler", "Detached house", "ngas", 0.9, 15, 3000, 0)
    dwelling1 = DwellingCategory("Detached house", heating1, 30)

    print(dwelling1.heatingSystem.name)
    

    heating2 = HeatingSystem("ASHP", "Detached house", "electricity", 2.5, 20, 15000, 0)
    dwelling1.heatingSystem = heating2
    print(dwelling1.heatingSystem.name)

    dwelling1.annualHeatDemand = 100
    print(dwelling1.annualHeatDemand)