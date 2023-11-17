
from costCurve import CostCurve
import numpy as np
from heatingSystem import HeatingSystem

class DwellingCategory():

    def __init__(self,dwellingType, heatingSystem, numberOfUnit,currentEPC, potentialEPC, currentHeatDemand, potentialHeatDemand, costEEImprovements, currentYear):
        self.avgCumulativeCost = 0
        self.avgCumulativeAmountOfIncentivesReceived = 0
        
        self.numberOfUnit = numberOfUnit
        self.ownership = "basic"
        self.dwellingType = dwellingType
        self.heating = ""
        self.heatingSystem = heatingSystem

        self.creationYear = currentYear
        self.currentYear = currentYear

        self.previousHeatingSystem = None
        
        self.currentEPCRating = currentEPC
        self.potentialEPCRating = potentialEPC
        self.initialEPCRating = self.currentEPCRating
        self.pastEnergyEfficiencyImprovements = 0 #in %, by how much the energy efficiency of this dwelling has been improved in the past
        
        self.potentialAvgAnnualHeatDemand = potentialHeatDemand
        self.currentAvgAnnualHeatDemand = currentHeatDemand # average annual heat demand for this dwelling category
        self.initialAvgAnnualHeatDemand = self.currentAvgAnnualHeatDemand
        self.kWhByEPCrating = (self.initialAvgAnnualHeatDemand-self.potentialAvgAnnualHeatDemand)/(self.potentialEPCRating-self.currentEPCRating) # heat demand savings (kWh) by EPC points

        self.listHeatingSystemTurnOver = self.initialiseList(self.numberOfUnit, self.heatingSystem.lifespan) # For dwellings in 2018, the heating systems are assumed to have been installed linearly
        self.listEnergyEfficiencyTurnOver = self.shiftList(self.listHeatingSystemTurnOver) # number of dwellings eligible for EE measures every year

        self.listEnergyEfficiencyTarget = self.initialiseList(self.numberOfUnit, (2035-2018)) #by 2035 all the dwellings need to reach their potential EPC
        self.listHeatingSystemTarget = self.initialiseList(self.numberOfUnit, (2050-2018)) #by 2050 all the dwellings need to use low carbon heating technology

        self.heatingSystemFlag = self.getHeatingSystemFlag() #True if the dwelling is eligible to change its heating system

        self.dwellingCategoryCostCurve = CostCurve(costEEImprovements/(self.currentAvgAnnualHeatDemand-self.potentialAvgAnnualHeatDemand), "linear")

        print("New dwelling category was created: {0} with {1}".format(dwellingType, heatingSystem.name))
        self.currentOPEX = 0
        

    def initialiseList(self, value, timeHorizon):
        nUnit = value
        finalList = [0]* timeHorizon
        tempValue = round(nUnit/timeHorizon, 0)
        for ii in range(0, timeHorizon):
            if ii == (timeHorizon-1):
                finalList[ii] = int(nUnit)
            else:
                finalList[ii] = int(tempValue)
            nUnit = nUnit - tempValue

        return finalList

    def shiftList(self, listInput):
        listOutput = listInput[1:]+[listInput[0]]
        return listOutput

    def updateListHeatingSystemTurnOver(self, value):
        self.listHeatingSystemTurnOver[0] = self.listHeatingSystemTurnOver[0] - value

    def updateListsAfterChangeOfHeatingSystem(self, value):
        # Dwellings which switched heating systems are removed from the lists
        self.listHeatingSystemTurnOver[0] = self.listHeatingSystemTurnOver[0] - value
        self.listEnergyEfficiencyTurnOver[-1] = self.listEnergyEfficiencyTurnOver[-1] - value
        

    # Store the year when the heating systems are reaching their end of life.  
    # Used after a change of heating system for the new dwelling

    def setListsAfterChangeOfHeatingSystem(self, value):
        # Dwellings in the next year will be available to change their heating systems
        self.listHeatingSystemTurnOver = [0] * self.heatingSystem.lifespan
        self.listHeatingSystemTurnOver[0] = value
        # Dwellings will be available to improve their energy efficiency next at the end of the turnover cycle (e.g., lifespan of the heating system)
        self.listEnergyEfficiencyTurnOver = [0] * self.heatingSystem.lifespan
        self.listEnergyEfficiencyTurnOver[-1] = value
    

    # to call after energy efficiency improvements for the new dwelling created
    def setListsAfterEEImprovements(self, value):
        # Dwellings in the next year will be available to change their heating systems
        self.listHeatingSystemTurnOver = [0] * self.heatingSystem.lifespan
        self.listHeatingSystemTurnOver[1] = value
        # Dwellings will be available to improve their energy efficiency next at the end of the turnover cycle (e.g., lifespan of the heating system)
        self.listEnergyEfficiencyTurnOver = [0] * self.heatingSystem.lifespan
        self.listEnergyEfficiencyTurnOver[0] = value
        self.listEnergyEfficiencyTarget = [0] * len(self.listEnergyEfficiencyTarget)


    # to call after energy efficiency improvements for the current dwelling created
    def updateListsAfterEEImprovements(self, value):
        # Dwellings with EE improvements are removed from the lists
        self.listHeatingSystemTurnOver[1] = self.listHeatingSystemTurnOver[1] - value
        self.listEnergyEfficiencyTurnOver[0] = self.listEnergyEfficiencyTurnOver[0] - value
        self.listEnergyEfficiencyTarget[0] = self.listEnergyEfficiencyTarget[0] - value
        self.listHeatingSystemTarget[1] = self.listHeatingSystemTarget[1] - value

    @property
    def numberOfUnit(self):
        return self._numberOfUnit

    @numberOfUnit.setter
    def numberOfUnit(self, value):
        self._numberOfUnit = value
        

    def updateCumulativeCost(self, numberOfNewSystems, discountRate, currentYear):
        self.avgCumulativeCost = self.avgCumulativeCost + self.heatingSystem.calcCAPEX(discountRate, currentYear) * numberOfNewSystems / self.numberOfUnit #Add capex of the new heating system to the cumulative cost

    def incrementCumulativeCost(self):
        self.avgCumulativeCost = self.avgCumulativeCost + self.currentOPEX

    def incrementYear(self):
        self.listHeatingSystemTurnOver = self.shiftList(self.listHeatingSystemTurnOver) 
        self.listEnergyEfficiencyTurnOver = self.shiftList(self.listEnergyEfficiencyTurnOver) 
        self.listEnergyEfficiencyTarget = self.shiftList(self.listEnergyEfficiencyTarget) 
        self.listHeatingSystemTarget = self.shiftList(self.listHeatingSystemTarget) 

    @property
    def currentOPEX(self):
        return self._currentOPEX

    @currentOPEX.setter
    def currentOPEX(self, value):
        self._currentOPEX = value

    def calcCurrentOPEX(self, fuelPrices, discountRate, currentYear):
        fuel = self.heatingSystem.fuel
        fuelPrice = fuelPrices[fuel]
        value = self.heatingSystem.calcTotalOPEX(self.currentAvgAnnualHeatDemand, fuelPrice, discountRate, currentYear)
        self.currentOPEX = value

    def getCheapestNewHeatingSystem(self, dictHeatingSystems,discountRate, currentYear, fuelPrices, timeHorizon, method):
        fuel = self.heatingSystem.fuel
        fuelPrice = fuelPrices[fuel]
        minCost = self.heatingSystem.calcCost(method, self.currentAvgAnnualHeatDemand, fuelPrice, discountRate, timeHorizon, currentYear)
        
        print('The {0} of this dwelling with the current heating system ({1}) is: £{2:,.0f}.'.format(method ,self.heatingSystem.name, minCost))

        heatingSystemsEligible = ["ASHP", "GSHP", "Resistance heating"]
        keyCheaperHeatingSystem = -1
        for k, v in dictHeatingSystems.items():
            if v.targetDwelling == self.dwellingType and v.name != self.heatingSystem.name and v.name in heatingSystemsEligible:
                fuel = v.fuel
                fuelPrice = fuelPrices[fuel]
                tempCost = v.calcCost(method, self.currentAvgAnnualHeatDemand, fuelPrice, discountRate, timeHorizon, currentYear)
                if tempCost<minCost:
                    keyCheaperHeatingSystem = k
                    minCost = tempCost
                print('The {0} of this dwelling with a new {1} is: £{2:,.0f}.'.format(method, v.name, tempCost))

        return keyCheaperHeatingSystem

    def implementEnergyEfficiencyImprovements(self, percentageImprovements, discountRate, currentYear):

        print('     The energy efficiency of this new dwelling is improved to {0:0.0f}% compared to the initial level.'.format(percentageImprovements*100))

        totalHeatSaving = round(percentageImprovements * (self.initialAvgAnnualHeatDemand - self.potentialAvgAnnualHeatDemand), 0)
        currentHeatSaving = round(self.initialAvgAnnualHeatDemand - self.currentAvgAnnualHeatDemand, 0) # equal to 0 if no previus EE improvements have been done
        
        self.currentAvgAnnualHeatDemand = int(round(self.initialAvgAnnualHeatDemand - totalHeatSaving, 0)) #Update the current average annual heat demand of the dwelling
        print('     The initial annual heat demand was {0}, the new annual heat demand is {1}.'.format(self.initialAvgAnnualHeatDemand, self.currentAvgAnnualHeatDemand))
        capex = self.dwellingCategoryCostCurve.calcCost(totalHeatSaving) - self.dwellingCategoryCostCurve.calcCost(currentHeatSaving)
        capex = self.calcCurrentYearCost(capex, discountRate, currentYear)
        self.avgCumulativeCost = self.avgCumulativeCost + capex # increase the avg cumulative cost value associated with the dwelling

        self.currentEPCRating = totalHeatSaving/self.kWhByEPCrating + self.initialEPCRating
        print('     The initial EPC rating was {0:.0f}, the new EPC rating is {1:.0f}.'.format(self.initialEPCRating, self.currentEPCRating))
        self.heatingSystemFlag = self.getHeatingSystemFlag()
        self.pastEnergyEfficiencyImprovements = percentageImprovements
        
        return True

    def calcCostEnergyEfficiencyImprovements(self, percentageImprovements, discountRate, currentYear, fuelPrices, timeHorizon, method):

        costEEImprovements=0
        opexSaved=0

        if self.currentAvgAnnualHeatDemand > self.potentialAvgAnnualHeatDemand:
            if percentageImprovements>self.pastEnergyEfficiencyImprovements:
                totalHeatSaving = round(percentageImprovements * (self.initialAvgAnnualHeatDemand - self.potentialAvgAnnualHeatDemand), 0)
                currentHeatSaving = round(self.initialAvgAnnualHeatDemand - self.currentAvgAnnualHeatDemand, 0) # equal to 0 if no previus EE improvements have been done
                
                fuel = self.heatingSystem.fuel
                fuelPrice = fuelPrices[fuel]

                tempCost = self.dwellingCategoryCostCurve.calcCost(totalHeatSaving) - self.dwellingCategoryCostCurve.calcCost(currentHeatSaving)
                tempCost = self.calcCurrentYearCost(tempCost, discountRate, currentYear)

                opexSaved = self.calcCurrentYearCost((totalHeatSaving-currentHeatSaving) / self.heatingSystem.efficiencyHeat * fuelPrice, discountRate, currentYear)

                if method == "EAC":
                    costEEImprovements = self.calcEACEnergyEfficiency(tempCost, discountRate, timeHorizon)
                elif method == "NPV":
                    costEEImprovements = self.calcNPVEnergyEfficiency(tempCost, opexSaved, discountRate, timeHorizon)
                else:
                    raise ValueError('Error: Method ({0}) is not a recognised method'.format(method))
                    
                print('The {0} to improve the EE to {1:0.0f}% (or {2:0.0f} kWh) is {3:0.0f}, the opex saved is {4:0.0f}.'.format(method, percentageImprovements*100,(totalHeatSaving-currentHeatSaving), costEEImprovements, opexSaved))          

        else:
            print("This is not possible to improve the energy efficiency by {0:0.0f}% as no further improvements can be implemented.".format(percentageImprovements*100))

        return costEEImprovements, opexSaved

    def calcCurrentYearCost(self, value, discountRate, currentYear):
        return value * np.power(1+discountRate,-currentYear)

    def calcNPVEnergyEfficiency(self, capex, opex, discountRate, timeHorizon):

        return (-capex+opex) + opex*(1-np.power((1+discountRate),- timeHorizon))/discountRate

    def calcEACEnergyEfficiency(self, capex, discountRate, timeHorizon):
        #print('EAC')
        return capex*discountRate/(1-np.power((1+discountRate),- timeHorizon))

    def getHeatingSystemFlag(self):
        # if EPC > C or potential EPC reached
        # EPC C is equivalent to EPC rating >= 69
        heatingSystemFlag = False
        if self.currentEPCRating >= 69:
            heatingSystemFlag = True
        if self.currentEPCRating == self.potentialEPCRating:
            heatingSystemFlag = True

        if heatingSystemFlag:
            print('     This new dwelling category is eligible for heat pumps.')
        else:
            print('     This new dwelling category is not eligible for heat pumps.')
        return heatingSystemFlag

    @property
    def heatingSystem(self):
        #print('Return current heating system')
        return self._heatingSystem


    @heatingSystem.setter
    def heatingSystem(self, value):
        if not isinstance(value, HeatingSystem):
            raise TypeError('Expected a HeatingSystem object')
        #print('This new dwelling has a new heating system installed: {0}'.format(value.name))
        self._heatingSystem = value


    @property
    def previousHeatingSystem(self):
        #print('Return current heating system')
        return self._previousHeatingSystem


    @previousHeatingSystem.setter
    def previousHeatingSystem(self, value):
        self._previousHeatingSystem = value

    @property
    def currentAvgAnnualHeatDemand(self):
        return self._annualHeatDemand

    @currentAvgAnnualHeatDemand.setter
    def currentAvgAnnualHeatDemand(self, value):
        # print('Setting new annual heat demand')
        value = self.checkNumberValue(value)
        if value < 0:
            raise ValueError('currentAvgAnnualHeatDemand less than 0 is not possible')
        self._annualHeatDemand = value


    @property
    def numberOfUnit(self):
        return self._numberOfUnit

    @numberOfUnit.setter
    def numberOfUnit(self, value):
        # print('Setting new annual heat demand')
        value = self.checkNumberValue(value)
        if value < 0:
            raise ValueError('numberOfUnit less than 0 is not possible')
        self._numberOfUnit = value


    def checkNumberValue(self, value):
        if isinstance(value, float):
            value = int(round(value, 0))

        if not isinstance(value, int):
            raise TypeError('Expected a integer')

        return value



    def totalAnnualHeatDemand(self):
        return self.currentAvgAnnualHeatDemand * self.numberOfUnit



if __name__ == '__main__':
    heating1 = HeatingSystem("Gas boiler", "Detached house", "ngas", 0.9, 15, 3000, 0)
    dwelling1 = DwellingCategory("Detached house", heating1, 30)

    print(dwelling1.heatingSystem.name)
    

    heating2 = HeatingSystem("ASHP", "Detached house", "electricity", 2.5, 20, 15000, 0)
    dwelling1.heatingSystem = heating2
    print(dwelling1.heatingSystem.name)

    dwelling1.currentAvgAnnualHeatDemand = 100
    print(dwelling1.currentAvgAnnualHeatDemand)