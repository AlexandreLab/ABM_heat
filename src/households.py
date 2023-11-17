from dwellingCategory import DwellingCategory
from heatingSystem import HeatingSystem
import pandas as pd
import numpy as np
import copy
import os
from pathlib import Path

## to use with anaconda:
# launch anaconda terminal
# type: code -- to launch VScode


# Model of the residential building stock
class Households():
    def __init__(self,busbar, dfDwellingsCategories, dfHeatingSystems, dfElectricityForHeatProfiles, method):

        self.dfElectricityForHeatProfiles = dfElectricityForHeatProfiles #dataframe of half-hourly profiles for resistance heater, ASHPs, GSHPs, etc.
        self.discountRate = 0.07
        self.listValidHeatingSystems = ["Gas boiler", "ASHP", "GSHP", "Resistance heating", "Oil boiler", "Biomass boiler"]
        self.listValidDwellingTypes = ["Detached house", "Semi-detached house", "Terraced house", "Flat"]
        self.fuelPrices = {}
        self.busbar = busbar
        self.method = method
        self.results = pd.DataFrame(columns=["Year", "Heating_system", "Dwelling_type","EPC_rating", "Number_of_unit", "Cumulative_cost_[£]","Cumulative_incentives_[£]", "Heat_demand_[kWh]"])

        self.currentYear = 0

        self.dictHeatingSystems = self.importHeatingSystems(dfHeatingSystems)
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

    def importHeatingSystems(self, dfHeatingSystems):
        print('Import heating systems...')
        # heatingSystems = ["Gas boiler", "ASHP", "Resistance heater"]
        # dwellingTypes = ["Detached house", "Detached house", "Detached house"]
        # dictCAPEXheating = {"Gas boiler": 3000, "ASHP": 10000, "Resistance heater": 2500,} #£
        # dictEfficiencyHeat = {"Gas boiler": 0.9, "ASHP": 2.5, "Resistance heater": 1} #£
        # fuelHeatingSystems = {"Gas boiler": "ngas", "Resistance heater": "electricity", "ASHP":"electricity"}

        dictHeatingSystems = {}
        for ii, row in dfHeatingSystems.iterrows():

            print(ii, row)
            heatingSystem = row["Technology"]
            fuel = row["Main fuel"].lower()
            dwellingType = row["Dwelling type"]
            capex = row["Capex [GBP/unit]"]
            effHeat = row["Efficiency heat"]
            opex = row["Fixed O&M (excluding elecricity) [GBP/year]"]
            lifespan = 12 # replacement lifetime is assumed to be below the technical lifetime. row["Technical lifetime [years]"]

            if heatingSystem in self.listValidHeatingSystems:

                tempHeatingSystem = HeatingSystem(heatingSystem, dwellingType, fuel, effHeat, lifespan, capex, opex)
                dictHeatingSystems[ii] = tempHeatingSystem
        return dictHeatingSystems

    # Return the heating system object based on the heating system name and dwelling type
    def getHeatingSystem(self, heatingSystemName, dwellingType):
        currentHeatingSystem = None
        successfulSearch = False
        print('looking for the heating system object to associate with {0} with {1}'.format(heatingSystemName,dwellingType))
        for s in self.dictHeatingSystems.values():
            if s.name == heatingSystemName and s.targetDwelling == dwellingType:
                currentHeatingSystem = s
                successfulSearch = True

        print(successfulSearch)
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
            currentEPC = row["CURRENT_ENERGY_EFFICIENCY"]
            potentialEPC = row["POTENTIAL_ENERGY_EFFICIENCY"]
            currentHeatDemand = row["Average heat demand before energy efficiency measures (kWh)"]
            potentialHeatDemand = row["Average heat demand after energy efficiency measures (kWh)"]
            costsOfEE = row["Average energy efficiency improvements costs (GBP)"]
            newDwelling = DwellingCategory(dwellingType, currentHeatingSystem, numberOfUnits, currentEPC, potentialEPC, currentHeatDemand, potentialHeatDemand, costsOfEE, self.currentYear)
            listDwellingCategories.append(newDwelling)
        return listDwellingCategories

    # Remove the dwelling categories with a number of unit equals to 0
    def cleanListDwellingCategories(self):
        cleanList =[]
        for d in self.listDwellingCategories:
            if d.numberOfUnit>0:
                cleanList.append(d)

        self.listDwellingCategories = cleanList
        return True

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

    def tryEnergyEfficiencyImprovements(self, dwelling, timeHorizon):
        print('Looking to improve the energy efficiency of this dwelling... ')

        if dwelling.listEnergyEfficiencyTurnOver[0] > 0: #number of dwellings that are eligible to have their EE improved

            maxPercentageSaving = 0
            for percentageSaving in [1]: #possible range of energy efficiency improvements [0.5, 0.8, 1.0] ==> 50%, 80% and 100% (not fully tested with efficiency improvement below 100%)

                EACmeasures, opexSaved = dwelling.calcCostEnergyEfficiencyImprovements(percentageSaving, self.discountRate, self.currentYear, self.fuelPrices, timeHorizon, self.method)
                if opexSaved - EACmeasures >= 0 and opexSaved>0 and EACmeasures>0:
                    maxPercentageSaving = percentageSaving

            newDwellingNumber = 0
            incentives = 0
            if maxPercentageSaving > 0: #Implement the energy efficiency improvements, no incentives/grants required
                newDwellingNumber = dwelling.listEnergyEfficiencyTurnOver[0]
            else:
                # Energy efficiency improvements are too expensive, incentives/grants from the governement are required to reach the target
                if maxPercentageSaving == 0 and dwelling.pastEnergyEfficiencyImprovements == 0 and dwelling.listEnergyEfficiencyTarget[0]>0:
                    print('Calculate amount of help from governement required')
                    NPVmeasures, opexSaved = dwelling.calcCostEnergyEfficiencyImprovements(1.0, self.discountRate, self.currentYear, self.fuelPrices, timeHorizon, "NPV")
                    if NPVmeasures<0:
                        if dwelling.listEnergyEfficiencyTarget[0]>dwelling.listEnergyEfficiencyTurnOver[0]:
                            newDwellingNumber = dwelling.listEnergyEfficiencyTurnOver[0]
                        else:
                            newDwellingNumber = dwelling.listEnergyEfficiencyTarget[0]
                        maxPercentageSaving = 1.0
                        incentives = -NPVmeasures

            if newDwellingNumber > 0:
                newDwelling = self.createNewDwelling(dwelling,newDwellingNumber , True)

                print('A new dwelling category is created: {0} with a {1}, created in year {2:d}'.format(newDwelling.dwellingType, newDwelling.heatingSystem.name, newDwelling.creationYear))
                print('     It has {0:d} units.'.format(newDwelling.numberOfUnit))
                newDwelling.implementEnergyEfficiencyImprovements(maxPercentageSaving, self.discountRate, self.currentYear)
                newDwelling.avgCumulativeAmountOfIncentivesReceived = newDwelling.avgCumulativeAmountOfIncentivesReceived + incentives
                self.listDwellingCategories.append(newDwelling)
            else:
                print('The energy efficiency of the dwelling is not improved.')
        else:
            print('There is no dwelling ready to have their energy efficiency improved.')

    def createNewDwelling(self, orgDwelling, numberNewDwelling, EEimprovements):
        newDwelling = copy.deepcopy(orgDwelling)
        newDwelling.numberOfUnit = numberNewDwelling
        newDwelling.creationYear = self.currentYear
        orgDwelling.numberOfUnit = max([int(round(orgDwelling.numberOfUnit-numberNewDwelling,0)), 0]) # updating the number of unit

        if EEimprovements:

            orgDwelling.updateListsAfterEEImprovements(numberNewDwelling)
            newDwelling.setListsAfterEEImprovements(numberNewDwelling)
        else:
            orgDwelling.updateListsAfterChangeOfHeatingSystem(numberNewDwelling)
            newDwelling.setListsAfterChangeOfHeatingSystem(numberNewDwelling)

        return newDwelling

    def tryChangingHeatingSystem(self, dwelling, timeHorizon): #timHorizon only used for the NPV calculations
        print('Looking to change the heating system of this dwelling... ')
        if dwelling.listHeatingSystemTurnOver[0] > 0:
            newDwellingNumber = dwelling.listHeatingSystemTurnOver[0]
            if dwelling.heatingSystemFlag:

                keyCheaperHeatingSystem = dwelling.getCheapestNewHeatingSystem(self.dictHeatingSystems, self.discountRate, self.currentYear, self.fuelPrices, timeHorizon, self.method)

                #Look at replacing the current heating systemName with a cheaper option
                if keyCheaperHeatingSystem>=0:

                    newHeatingSystem = self.dictHeatingSystems[keyCheaperHeatingSystem]
                    #print('The best heating system identified is: {0}'.format(newHeatingSystem.name))

                    newDwelling = self.createNewDwelling(dwelling, newDwellingNumber, False)
                    newDwelling.heatingSystem = newHeatingSystem #changing the heating systemName of the new dwelling category
                    newDwelling.updateCumulativeCost(newDwelling.numberOfUnit, self.discountRate, self.currentYear) # Add CAPEX costs to the cumulative costs
                    newDwelling.previousHeatingSystem = dwelling.heatingSystem

                    self.listDwellingCategories.append(newDwelling)
                    print('A new dwelling category is created: {0} with a {1}, created in year {2:d}'.format(newDwelling.dwellingType, newDwelling.heatingSystem.name, newDwelling.creationYear))
                    print('     {0:,d} {1}s with {2}s are switching to {3}s'.format(newDwelling.numberOfUnit, dwelling.dwellingType, dwelling.heatingSystem.name, newHeatingSystem.name))
                else:
                    print('The current heating system is the cheapest option')
                    # The current heating system is the cheapest. The lifespan of a share of the dwelling has ended thus their heating systems need to be replaced
                    # the CAPEX costs of the current heating systems is added to the cumulative costs
                    dwelling.updateCumulativeCost(newDwellingNumber, self.discountRate, self.currentYear)
            else:
                print('The dwelling is not eligible to change to another heating system.')
                dwelling.updateCumulativeCost(newDwellingNumber, self.discountRate, self.currentYear)

        else:
            print('There is no dwelling ready to switch to another heating system.')
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
            d.calcCurrentOPEX(self.fuelPrices,self.discountRate, self.currentYear)
            d.incrementCumulativeCost()
            d.incrementYear()
        self.currentYear = self.currentYear + 1
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
            tempResults.loc[ii, "EPC_rating"] = d.currentEPCRating
            tempResults.loc[ii, "Cumulative_incentives_[£]"] = d.avgCumulativeAmountOfIncentivesReceived

        tempResults = tempResults.groupby(["Year", "Heating_system", "Dwelling_type", "EPC_rating"]).sum().reset_index()

        self.results = pd.concat([self.results, tempResults], axis=0)
        return True


if __name__ == '__main__':

    method = 'EAC'

    # Extracting electricity for heat profiles for ASHP, GSHP and resistance heater
    dfHeatingProfiles = pd.read_csv(
        './data/HeatingSystemsProfiles/Half-hourly_profiles_of_heating_technologies.csv',
        index_col=0,
        parse_dates=True)
    elec_cols = [c for c in dfHeatingProfiles.columns if "_elec" in c]
    dfHeatingProfiles = dfHeatingProfiles[elec_cols]
    dfHeatingProfiles.columns = [
        c.replace('Normalised_', '').replace('_', ' ').replace('elec', '')
        for c in dfHeatingProfiles.columns
    ]

    #data about the residential sector

    path_input_data = "./data/ResidentialHeatSectorData"
    file = "input_data.csv"

    dfDwellings = pd.read_csv(path_input_data + os.path.sep + file)

    #import heating systems parameters and costs
    path_heating_data = r"D:\OneDrive - Cardiff University\04 - Projects\03 - PhD\03 - Analysis\11 - Optimisation"
    file = "technology_dataset - optimisation.xlsx"
    dfHeating = pd.read_excel(path_heating_data + os.path.sep + file,
                              sheet_name="Individual_tech")
    dfHeating = dfHeating.loc[dfHeating["Set"] == "2050 set", :]
    dfHeating["Dwelling type"] = [
        c.capitalize() + " house" if "Flat" not in c.capitalize() else c
        for c in dfHeating["Dwelling type"]
    ]

    housholdsGroup1 = Households(1, dfDwellings, dfHeating, dfHeatingProfiles,
                                 method)

    #import fuel prices data from https://www.gov.uk/government/publications/updated-energy-and-emissions-projections-2019
    file = "fuel_prices.csv"
    dfFuelPrices = pd.read_csv(path_input_data + os.path.sep + file,
                               index_col=0)

    dfFuelPrices.columns = dfFuelPrices.columns.astype(int)

    for year in range(2018, 2035, 1):  #dfFuelPrices.columns[-1]
        print('-----------------------------------------------')
        print('year: {0}'.format(year))
        print('-----------------------------------------------')
        tempFuelPrices = {
            'electricity': dfFuelPrices.loc["electricity", year] / 100,
            'ngas': dfFuelPrices.loc["ngas", year] / 100,
            'biomass': dfFuelPrices.loc["biomass", year] / 100,
            'oil': dfFuelPrices.loc["oil", year] / 100,
        }  # converted to £/kWh
        housholdsGroup1.fuelPrices = tempFuelPrices
        print(housholdsGroup1.fuelPrices)
        numberOfDwellingCategories = len(
            housholdsGroup1.listDwellingCategories)
        for ii in range(0, numberOfDwellingCategories):
            d = housholdsGroup1.listDwellingCategories[ii]
            print('*******')

            print('{0} with a {1}, created in year {2:d}'.format(
                d.dwellingType, d.heatingSystem.name, d.creationYear))
            print('EE targets:')
            print(d.listEnergyEfficiencyTarget,
                  np.sum(d.listEnergyEfficiencyTarget))
            # Try to improve the energy efficiency of dwellings first
            #average lifetime of energy efficiency measures is assumed to be 15 years
            print(d.listEnergyEfficiencyTurnOver,
                  np.sum(d.listEnergyEfficiencyTurnOver))
            housholdsGroup1.tryEnergyEfficiencyImprovements(d, 15)

            # Try to change the heating systems of dwellings next
            print('{0} with a {1}, created in year {2:d}'.format(
                d.dwellingType, d.heatingSystem.name, d.creationYear))
            print(d.listHeatingSystemTurnOver,
                  np.sum(d.listHeatingSystemTurnOver))
            value = housholdsGroup1.tryChangingHeatingSystem(d, 5)

            #print(d.listEnergyEfficiencyTurnOver, np.sum(d.listEnergyEfficiencyTurnOver), d.energyEfficiencyTurnOver)
            #print(d.listHeatingSystemTurnOver, np.sum(d.listHeatingSystemTurnOver), d.heatingSystemTurnOver)

        housholdsGroup1.calcNumberOfDwellings()
        housholdsGroup1.calcEndOfYear()
        housholdsGroup1.cleanListDwellingCategories()
        housholdsGroup1.storeResults(year)

    print(housholdsGroup1.results)
    path_save = r'D:\OneDrive - Cardiff University\04 - Projects\18 - ABM\01 - Code\Results_for_notebooks'
    housholdsGroup1.results.to_csv(path_save + os.path.sep +
                                   "resultsSouthWales.csv")


def test_function():
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
        print('-----------------------------------------------')
        print('year: {0}'.format(year))
        print('-----------------------------------------------')
        tempFuelPrices = {'electricity': dictFuelPrices["electricity"][year], 'ngas':dictFuelPrices['ngas'][year]}
        housholdsGroup1.fuelPrices = tempFuelPrices
        print(housholdsGroup1.fuelPrices)
        numberOfDwellingCategories = len(housholdsGroup1.listDwellingCategories)
        for ii in range(0, numberOfDwellingCategories):
            d = housholdsGroup1.listDwellingCategories[ii]
            print('*******')

            print('{0} with a {1}, created in year {2:d}'.format(d.dwellingType, d.heatingSystem.name, d.creationYear))

            # Try to improve the energy efficiency of dwellings first
            #average lfietime of energy efficiency measures is assumed to be 15 years
            print(d.listEnergyEfficiencyTurnOver, np.sum(d.listEnergyEfficiencyTurnOver), d.energyEfficiencyTurnOver)
            housholdsGroup1.tryEnergyEfficiencyImprovements(d, 15)

            # Try to change the heating systems of dwellings next
            print('{0} with a {1}, created in year {2:d}'.format(d.dwellingType, d.heatingSystem.name, d.creationYear))
            print(d.listHeatingSystemTurnOver, np.sum(d.listHeatingSystemTurnOver), d.heatingSystemTurnOver)
            value = housholdsGroup1.tryChangingHeatingSystem(d, 5)

            print(d.listEnergyEfficiencyTurnOver, np.sum(d.listEnergyEfficiencyTurnOver), d.energyEfficiencyTurnOver)
            print(d.listHeatingSystemTurnOver, np.sum(d.listHeatingSystemTurnOver), d.heatingSystemTurnOver)

        housholdsGroup1.calcNumberOfDwellings()
        housholdsGroup1.calcEndOfYear()
        housholdsGroup1.cleanListDwellingCategories()
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
