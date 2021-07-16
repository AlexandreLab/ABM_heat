from dwellingCategory import DwellingCategory
from heatingSystem import HeatingSystem
import pandas as pd
import numpy as np
import copy
import os

## to use with anaconda:
# launch anaconda terminal
# type: code to launch VScode


# Model of the residential building stock
class Households():
    def __init__(self,busbar, dfDwellingsCategories, dfElectricityForHeatProfiles, method):
        
        self.dfElectricityForHeatProfiles = dfElectricityForHeatProfiles #dataframe of half-hourly profiles for resistance heater, ASHPs, GSHPs, etc.
        self.discountRate = 0.07
        self.listValidHeatingSystems = ["Gas boiler", "ASHP", "GSHP", "Resistance heater", "Oil boiler", "Biomass boiler"]
        self.listValidDwellingTypes = ["Detached house", "Semi-detached house", "Terraced house", "Flat"]
        self.fuelPrices = {"ngas": 0.02, "electricity": 0.14} #£/kWh
        self.busbar = busbar
        self.method = method
        self.results = pd.DataFrame(columns=["Year", "Heating_system", "Dwelling_type", "Number_of_unit", "Cumulative_cost_[£]", "Heat_demand_[kWh]"])

        self.dictHeatingSystems = self.importHeatingSystems()
        self.listDwellingCategories = self.importDwellingCategories(dfDwellingsCategories)
        print('................................................................')
        print('Initialisation of the model completed')
        print('................................................................')


    @property
    def fuelPrices(self):
        return self._fuelPrices

    @fuelPrices.setter
    def fuelPrices(self, value):
        self._fuelPrices = value

    def importHeatingSystems(self):
        print('Import heating systems...')
        heatingSystems = ["Gas boiler", "ASHP", "Resistance heater"]
        dwellingTypes = ["Detached house", "Detached house", "Detached house"]
        dictCAPEXheating = {"Gas boiler": 3000, "ASHP": 10000, "Resistance heater": 2500} #£
        dictEfficiencyHeat = {"Gas boiler": 0.9, "ASHP": 2.5, "Resistance heater": 1} #£
        fuelHeatingSystems = {"Gas boiler": "ngas", "Resistance heater": "electricity", "ASHP":"electricity"}
        
        dictHeatingSystems = {}
        for ii, systemName in enumerate(heatingSystems):
            dwellingType = dwellingTypes[ii]

            if dwellingType not in self.listValidDwellingTypes:
                raise ValueError("{0} is not a valid dwelling type".format(dwellingType))

            fuel = fuelHeatingSystems[systemName]
            capex = dictCAPEXheating[systemName]
            effHeat = dictEfficiencyHeat[systemName]
            opex = 0
            tempHeatingSystem = HeatingSystem(systemName, dwellingType, fuel, effHeat, 15, capex, opex)

            dictHeatingSystems[ii] = tempHeatingSystem
        return dictHeatingSystems

    # Return the heating system object based on the heating system name and dwelling type
    def getHeatingSystem(self, heatingSystemName, dwellingType):
        currentHeatingSystem = None
        for s in self.dictHeatingSystems.values():
            if s.name == heatingSystemName and s.targetDwelling == dwellingType:
                currentHeatingSystem = s
        return currentHeatingSystem


    def importDwellingCategories(self, dfDwellingCategories):

        if not isinstance(dfDwellingCategories, pd.DataFrame):
            raise ValueError("The input parameters to importDwellingCategories is not a dataframe instance")

        print('Import dwelling stocks characteristics...')
        listDwellingCategories = []
        for ii, row in dfDwellingCategories.iterrows():
            dwellingType = row["DwellingType"]
            heatingSystemName = row["HeatingSystem"]
            currentHeatingSystem = self.getHeatingSystem(heatingSystemName, dwellingType)
            numberOfUnits = row["NumberOfUnits"]

            if currentHeatingSystem is None:
                raise ValueError("No heating systemName matches, the inputs: {0} and {1}".format(heatingSystemName, dwellingType))

            if dwellingType not in self.listValidDwellingTypes:
                raise ValueError("{0} is not a valid dwelling type".format(dwellingType))

            if not ((isinstance(numberOfUnits, int) and numberOfUnits>=0)):
                raise ValueError("{0} is not a valid number of units".format(numberOfUnits))

            newDwelling = DwellingCategory(dwellingType, currentHeatingSystem, numberOfUnits)
            listDwellingCategories.append(newDwelling)
        return listDwellingCategories

    def calcHeatDemandByHeatingSystem(self):
        totalHeatDemand = {}
        for h in self.dictHeatingSystems.values():
            tempHeatDemand = 0
            for d in self.listDwellingCategories:
                if d.heatingSystem.name == h.name:
                    tempHeatDemand = tempHeatDemand + d.avgAnnualHeatDemand * d.numberOfUnit
            totalHeatDemand[h.name] = tempHeatDemand
        return totalHeatDemand


    def calcHeatDemandByFuel(self):
        totalHeatDemand = {}
        for fuel in self.fuelPrices.keys():
            tempHeatDemand= 0
            for d in self.listDwellingCategories:
                tempFuel = d.heatingSystem.fuel
                if tempFuel == fuel:
                    tempHeatDemand = tempHeatDemand + d.avgAnnualHeatDemand * d.numberOfUnit
            totalHeatDemand[fuel] = tempHeatDemand
        return totalHeatDemand


    def calcDwellingCategoryCost(self, dwelling, timeHorizon):
        print('{0} with a {1}'.format(dwelling.dwellingType, dwelling.heatingSystem.name))

        keyCheaperHeatingSystem = dwelling.getCheapestNewHeatingSystem(self.dictHeatingSystems, self.discountRate, self.fuelPrices, timeHorizon, self.method)

        #Look at replacing the current heating systemName with a cheaper option
        if keyCheaperHeatingSystem>=0:
            newHeatingSystem = self.dictHeatingSystems[keyCheaperHeatingSystem]
            print('The best heating system identified is: {0}'.format(newHeatingSystem.name))

            newDwelling = copy.deepcopy(dwelling)

            dwelling.numberOfUnit = max([int(round(dwelling.numberOfUnit-dwelling.heatingSystemTurnOver,0)), 0]) # updating the number of unit
            
            
            newDwelling.heatingSystem = newHeatingSystem #changing the heating systemName of the new dwelling category
            
            numberOfDwellingSwitching = newDwelling.numberOfUnit - dwelling.numberOfUnit
            print('{0:,d} {1}s with {2}s are switching to {3}s'.format(numberOfDwellingSwitching, dwelling.dwellingType, dwelling.heatingSystem.name, newHeatingSystem.name))
            newDwelling.numberOfUnit = numberOfDwellingSwitching # updating the number of unit
            newDwelling.updateCumulativeCost() # Add CAPEX costs to the cumulative costs
            newDwelling.previousHeatingSystem = dwelling.heatingSystem
            newDwelling.heatingSystemTurnOver = 0 # it is not possible for the dwellings that just switched to a new heating system to switch to another one

            self.listDwellingCategories.append(newDwelling)
            newDwelling.currentOPEX = 0
            dwelling.currentOPEX = 0
        else: print('The current heating system is the cheapest option')

        return True

    def getElectricityForHeatProfile(self):
        dictHeatDemand = self.calcHeatDemandByHeatingSystem()
        tempProfiles = self.dfElectricityForHeatProfiles.copy() 
        for k,v in dictHeatDemand.items():
            if k in tempProfiles.columns:
                tempProfiles[k] = tempProfiles[k] * v
        elecForHeatProfile = tempProfiles.sum(axis=1).values
        return elecForHeatProfile

    def calcNumberOfDwellings(self):
        numberOfDwellings = 0
        for d in self.listDwellingCategories:
            numberOfDwellings = numberOfDwellings + d.numberOfUnit

        print('there are {0} dwelling categories and {1:,d} dwellings in total'.format(len(self.listDwellingCategories), numberOfDwellings))

        return numberOfDwellings

    def calcEndOfYear(self):
        for ii,d in enumerate(self.listDwellingCategories):
            d.calcCurrentOPEX(self.fuelPrices)
            d.incrementCumulativeCost()
        return True

    def storeResults(self, currentYear):
        index = [c for c in range(0, len(self.listDwellingCategories))]
        columns = self.results.columns
        tempResults = pd.DataFrame(columns=columns, index=index)
        for ii,d in enumerate(self.listDwellingCategories):
            tempResults.loc[ii, "Year"] = currentYear
            tempResults.loc[ii, "Heating_system"] = d.heatingSystem.name
            tempResults.loc[ii, "Dwelling_type"] = d.dwellingType
            tempResults.loc[ii, "Number_of_unit"] = d.numberOfUnit
            tempResults.loc[ii, "Cumulative_cost_[£]"] = d.avgCumulativeCost * d.numberOfUnit
            tempResults.loc[ii, "Heat_demand_[kWh]"] = d.totalAnnualHeatDemand()
        tempResults = tempResults.groupby(["Year", "Heating_system", "Dwelling_type"]).sum().reset_index()

        self.results = pd.concat([self.results, tempResults], axis=0)
        return True


if __name__ == '__main__':

    method = 'EAC'

    # Extracing electricity for heat profiles for ASHP, GSHP and resistance heater
    dfHeatingProfiles = pd.read_csv('HeatingSystemsProfiles/Half-hourly_profiles_of_heating_technologies.csv', index_col=0, parse_dates=True)
    elec_cols = [c for c in dfHeatingProfiles.columns if "_elec" in c]
    dfHeatingProfiles = dfHeatingProfiles[elec_cols]
    dfHeatingProfiles.columns = [c.replace('Normalised_', '').replace('_', ' ').replace('elec','') for c in dfHeatingProfiles.columns]

    dfDwellings = pd.DataFrame(columns = ["DwellingType", "HeatingSystem", "NumberOfUnits"])
    dfDwellings["DwellingType"] = ["Detached house"]#, "Detached house", "Detached house"]
    dfDwellings["HeatingSystem"] = ["Gas boiler"]#, "Resistance heater", "ASHP"]
    dfDwellings["NumberOfUnits"] = [6000]#, 0, 0]
    housholdsGroup1 = Households(1, dfDwellings, dfHeatingProfiles, method)

    dictFuelPrices = {
        'electricity': {2018: 0.17, 2019: 0.2, 2020:0.2, 2021:0.2, 2022:0.2, 2023:0.2}, 
        'ngas': {2018: 0.04, 2019: 0.08, 2020:0.16, 2021:0.32, 2022:0.32, 2023:0.32}
        }

    #Year 1: Nothing changed during the first year
    housholdsGroup1.calcNumberOfDwellings()
    housholdsGroup1.calcEndOfYear()
    housholdsGroup1.storeResults(2018)

    for year in range(2019, 2024, 1):
        print('year: {0}'.format(year))
        tempFuelPrices = {'electricity': dictFuelPrices["electricity"][year], 'ngas':dictFuelPrices['ngas'][year]}
        housholdsGroup1.fuelPrices = tempFuelPrices
        print(housholdsGroup1.fuelPrices)
        numberOfDwellingCategories = len(housholdsGroup1.listDwellingCategories)
        for ii in range(0, numberOfDwellingCategories):
            d = housholdsGroup1.listDwellingCategories[ii]
            value = housholdsGroup1.calcDwellingCategoryCost(d, 5)
        housholdsGroup1.calcNumberOfDwellings()
        housholdsGroup1.calcEndOfYear()
        housholdsGroup1.storeResults(year)

    #print(housholdsGroup1.results)

    #Year 2: Looking at replacing the heating systems  
    # for d in housholdsGroup1.listDwellingCategories:
    #     value = housholdsGroup1.calcDwellingCategoryCost(d, "EAC")



    #Create the electricity for heat profiles to be added to the 2018 electricity demand
    # print(housholdsGroup1.getElectricityForHeatProfile())
    
    print(housholdsGroup1.results)
    path_save = r'D:\OneDrive - Cardiff University\04 - Projects\18 - ABM\01 - Code\Results_for_notebooks'
    housholdsGroup1.results.to_csv(path_save+os.path.sep+"results.csv")
    # print(housholdsGroup1.calcHeatDemandByHeatingSystem())
