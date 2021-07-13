from dwellingCategory import DwellingCategory
from heatingSystem import HeatingSystem
import pandas as pd
import numpy as npcond

## to use with anaconda:
# launch anaconda terminal
# type: code to launch VScode


# Model of the residential building stock
class Households():
    

    def __init__(self,busbar, dfDwellingsCategories, dfElectricityForHeatProfiles):
        
        self.dfElectricityForHeatProfiles = dfElectricityForHeatProfiles #dataframe of half-hourly profiles for resistance heater, ASHPs, GSHPs, etc.
        self.discountRate = 0.07
        self.listValidHeatingSystems = ["Gas boiler", "ASHP", "GSHP", "Resistance heater", "Oil boiler", "Biomass boiler"]
        self.listValidDwellingTypes = ["Detached house", "Semi-detached house", "Terraced house", "Flat"]
        self.fuelPrices = {"ngas": 0.02, "electricity": 0.14} #£/kWh
        self.busbar = busbar

        self.listHeatingSystems = self.importHeatingSystems()
        self.listDwellingCategories = self.importDwellingCategories(dfDwellingsCategories)
        print('................................................................')
        print('Initialisation of the model completed')
        print('................................................................')

    def importHeatingSystems(self):
        print('Import heating systems...')
        heatingSystems = ["Gas boiler", "ASHP", "Resistance heater"]
        dwellingTypes = ["Detached house", "Detached house", "Detached house"]
        dictCAPEXheating = {"Gas boiler": 3000, "ASHP": 8000, "Resistance heater": 1500} #£
        fuelHeatingSystems = {"Gas boiler": "ngas", "Resistance heater": "electricity", "ASHP":"electricity"}
        
        listHeatingSystems = []
        for ii, system in enumerate(heatingSystems):
            dwellingType = dwellingTypes[ii]

            if dwellingType not in self.listValidDwellingTypes:
                raise ValueError("{0} is not a valid dwelling type".format(dwellingType))

            fuel = fuelHeatingSystems[system]
            capex = dictCAPEXheating[system]
            opex = 0
            tempHeatingSystem = HeatingSystem(system, dwellingType, fuel, 0.9, 15, capex, opex)

            listHeatingSystems.append(tempHeatingSystem)
        return listHeatingSystems

    # Return the heating system object based on the heating system name and dwelling type
    def getHeatingSystem(self, heatingSystemName, dwellingType):
        currentHeatingSystem = None
        for s in self.listHeatingSystems:
            if s.name == heatingSystemName and s.targetDwelling == dwellingType:
                currentHeatingSystem = s
        return currentHeatingSystem


    def importDwellingCategories(self, dfDwellingCategories):
        print('Import dwelling stocks characteristics...')
        listDwellingCategories = []
        for ii, row in dfDwellingCategories.iterrows():
            dwellingType = row["DwellingType"]
            heatingSystemName = row["HeatingSystem"]
            currentHeatingSystem = self.getHeatingSystem(heatingSystemName, dwellingType)
            numberOfUnits = row["NumberOfUnits"]

            if currentHeatingSystem is None:
                raise ValueError("No heating system matches, the inputs: {0} and {1}".format(heatingSystemName, dwellingType))

            if dwellingType not in self.listValidDwellingTypes:
                raise ValueError("{0} is not a valid dwelling type".format(dwellingType))

            if not ((isinstance(numberOfUnits, int) and numberOfUnits>=0)):
                raise ValueError("{0} is not a valid number of units".format(numberOfUnits))

            newDwellingCategory = DwellingCategory(dwellingType, currentHeatingSystem, numberOfUnits)
            listDwellingCategories.append(newDwellingCategory)
        return listDwellingCategories

    def calcHeatDemandByHeatingSystem(self):
        totalHeatDemand = {}
        for h in self.listHeatingSystems:
            tempHeatDemand = 0
            for d in self.listDwellingCategories:
                if d.heatingSystem.name == h.name:
                    tempHeatDemand = tempHeatDemand + d.annualHeatDemand * d.numberOfUnit
            totalHeatDemand[h.name] = tempHeatDemand
        return totalHeatDemand


    def calcHeatDemandByFuel(self):
        totalHeatDemand = {}
        for fuel in self.fuelPrices.keys():
            tempHeatDemand= 0
            for d in self.listDwellingCategories:
                tempFuel = d.heatingSystem.fuel
                if tempFuel == fuel:
                    tempHeatDemand = tempHeatDemand + d.annualHeatDemand * d.numberOfUnit
            totalHeatDemand[fuel] = tempHeatDemand
        return totalHeatDemand


    def calcDwellingCategoryCost(self, dwelling, method):
        print('{0} with a {1}'.format(dwelling.dwellingType, dwelling.heatingSystem.name))
        
        currentHeatingSystem = dwelling.heatingSystem
        annualHeatDemand = dwelling.annualHeatDemand
        fuel = currentHeatingSystem.fuel
        fuelPrice = self.fuelPrices[fuel]
        currentCost = currentHeatingSystem.calcCost(method, annualHeatDemand, fuelPrice, self.discountRate)
        print('The dwelling {0} with the current heating system ({1}): £{2:,.0f}'.format(method ,currentHeatingSystem.name, currentCost))

        minCost = currentCost
        indexCheaperHeatingSystem = -1
        for ii, system in enumerate(self.listHeatingSystems):
            if system.targetDwelling == dwelling.dwellingType and system.name != currentHeatingSystem.name:
                tempCost = system.calcCost(method, annualHeatDemand, fuelPrice, self.discountRate)
                if tempCost<minCost:
                    indexCheaperHeatingSystem = ii
                    minCost = tempCost
                print('The dwelling {0} with a new {1} is: £{2:,.0f}'.format(method, system.name, tempCost))

        if indexCheaperHeatingSystem>=0:
            newHeatingSystem = self.listHeatingSystems[indexCheaperHeatingSystem]
            print('The new heating system identified is: {0}'.format(newHeatingSystem.name))
        else: print('The current heating system is the cheapest option')

        return True

    def scaleElectricityForHeatProfile(self):
        dictHeatDemand = self.calcHeatDemandByHeatingSystem()
        tempProfiles = self.dfElectricityForHeatProfiles.copy() 
        for k,v in dictHeatDemand.items():
            if k in tempProfiles.columns:
                tempProfiles[k] = tempProfiles[k] * v
        elecForHeatProfile = tempProfiles.sum(axis=1).values
        return elecForHeatProfile


if __name__ == '__main__':

    # Extracing electricity for heat profiles for ASHP, GSHP and resistance heater
    dfHeatingProfiles = pd.read_csv('HeatingSystemsProfiles/Half-hourly_profiles_of_heating_technologies.csv', index_col=0, parse_dates=True)
    elec_cols = [c for c in dfHeatingProfiles.columns if "_elec" in c]
    dfHeatingProfiles = dfHeatingProfiles[elec_cols]
    dfHeatingProfiles.columns = [c.replace('Normalised_', '').replace('_', ' ').replace('elec','') for c in dfHeatingProfiles.columns]

    dfDwellings = pd.DataFrame(columns = ["DwellingType", "HeatingSystem", "NumberOfUnits"])
    dfDwellings["DwellingType"] = ["Detached house", "Detached house", "Detached house"]
    dfDwellings["HeatingSystem"] = ["Gas boiler", "Resistance heater", "ASHP"]
    dfDwellings["NumberOfUnits"] = [1000, 2000, 3000]
    housholdsGroup1 = Households(1, dfDwellings, dfHeatingProfiles)

    for d in housholdsGroup1.listDwellingCategories:
        value = housholdsGroup1.calcDwellingCategoryCost(d, "EAC")

    print(housholdsGroup1.scaleElectricityForHeatProfile())

    # print(housholdsGroup1.calcHeatDemandByHeatingSystem())
