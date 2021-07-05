import random
from random import randint

from collections import namedtuple
import numpy as np
import pandas as pd
import math
import Utils


class policyMaker():
    
    
    def __init__(self):

        self.initialise()
        

    def initialise(self):
        file2 = open("BASEYEAR.txt", "r") 
        temp = file2.read()
        self.BASEYEAR = int(temp)
        file2.close()
        self.year=self.BASEYEAR

        carbonFilePath = 'CarbonPrice/carbonPrice'+str(self.BASEYEAR)+'_2050.txt'
        self.yearlyCarbonCost = Utils.loadTextFile(carbonFilePath)
        wholesaleElecFilePath = 'WholesaleEnergyPrices/ElectricityBaseLoad'+str(self.BASEYEAR)+'_2050_GBPPerkWh.txt'
        self.yearlyWholesalePrice = Utils.loadTextFile(wholesaleElecFilePath)
        self.curCO2Price = self.yearlyCarbonCost[0]
        
        self.yearEmissionsTarget = 50000000000 # 50Mt of CO2 ** ignore this
        self.minDeRateCapMargin = 10000000 # 25000000 # 25 GW
        self.maxDeRateCapMargin = 25000000 # 25 GW
        self.yearCO2IntensityTarget = 250 #100 # gCO2/kWh, 50-100 in https://www.current-news.co.uk/news/uk-powers-to-new-grid-carbon-intensity-low-of-just-32g-co2-kwh

        
        self.curCFDPrice = 0.0 
        self.yearlyCO2Price = list()
        self.yearlyCFDPrice = list()
        self.recordYearData()      
        self.name = 'Government'
        self.years = list()
        self.years.append(self.year)
        self.yearlyEmissionsIntensity = list()
        self.yearlyEmissTarget = list()

    # update values for next year
    def increaseYear(self):
        if(self.year<2018):
            self.yearCO2IntensityTarget = 250
        elif(self.year<=2050):
            CO2DecreaseFrac = (self.year - 2018)/(2050 - 2018)
            newCO2P = 250 - (CO2DecreaseFrac*250)
            self.yearCO2IntensityTarget = newCO2P
        else:
            self.yearCO2IntensityTarget = 0
                
        if((self.year+5)<2018):
            self.CO2Target5Years = 250
        elif((self.year + 5)<=2050):
            year5 = self.year + 5
            CO2DecreaseFrac = (year5 - 2018)/(2050 - 2018)
            newCO2P = 250 - (CO2DecreaseFrac*250)
            self.CO2Target5Years = newCO2P
        else:
            self.CO2Target5Years = 0
        self.year = self.year + 1
        self.years.append(self.year)

    '''
    # get next year CO2 price using emissions intensity
    def getNextYearCO2Price(self, emissionsIntense):
     #   print('new year ',self.year)
     #   print('emissionsIntense from last year (gCO2/kWh)',emissionsIntense)
     #   print('yearCO2IntensityTarget (gCO2/kWh)',self.yearCO2IntensityTarget)
        self.yearlyEmissionsIntensity.append(emissionsIntense)
        self.yearlyEmissTarget.append(self.yearCO2IntensityTarget)

        BEISProjectedPrice = self.yearlyCarbonCost[self.year-self.BASEYEAR]
        curCO2P = self.curCO2Price
        self.curCO2Price = curCO2P - curCO2P*(self.yearCO2IntensityTarget-emissionsIntense)/(random.randint(0,40)*self.yearCO2IntensityTarget)
        if(self.curCO2Price-curCO2P>80):
        	self.curCO2Price = curCO2P+80
        elif(curCO2P-self.curCO2Price>80):
        	self.curCO2Price  = curCO2P-80

        if (self.curCO2Price < 18):
            self.curCO2Price = 18
        elif(self.curCO2Price>300):
        	self.curCO2Price = 300
        return self.curCO2Price
        '''
    def getNextYearCO2Price(self, emissionsIntense):
        print('new year ',self.year)
        print('emissionsIntense from last year (gCO2/kWh)',emissionsIntense)
        print('yearCO2IntensityTarget (gCO2/kWh)',self.yearCO2IntensityTarget)
        self.yearlyEmissionsIntensity.append(emissionsIntense)
        self.yearlyEmissTarget.append(self.yearCO2IntensityTarget)

        if(emissionsIntense>self.CO2Target5Years): # now looking at the co2 target 5 years in the future
            BEISco2Price = self.yearlyCarbonCost[self.year-self.BASEYEAR]
            CO210PC = self.curCO2Price *1.1
            if(CO210PC > BEISco2Price):
                self.curCO2Price = CO210PC
            else:
                self.curCO2Price = BEISco2Price
            
        else:
            BEISco2Price = self.yearlyCarbonCost[self.year-self.BASEYEAR]
            curCO2 = self.curCO2Price
            if(curCO2>BEISco2Price):
                self.curCO2Price = curCO2
            else:
                self.curCO2Price = BEISco2Price
        
        return self.curCO2Price

    # ignore this function, its not used anywhere
    def getCFDPrice(self, deRatedCapMargin): # This is old, do not use this function
        y = self.year - self.BASEYEAR
        curWholesale = self.yearlyWholesalePrice[y]
        if(deRatedCapMargin<self.minDeRateCapMargin):
            self.curCFDPrice = self.curCFDPrice + 0.01
        
        elif(deRatedCapMargin>self.maxDeRateCapMargin):
            self.curCFDPrice = self.curCFDPrice - 0.01
            if(self.curCFDPrice<curWholesale):
                self.curCFDPrice = curWholesale
        
        else:
            self.curCFDPrice = self.curCFDPrice
        

        return self.curCFDPrice


    # estimate demand in a specific year
    def estimateDemandYear(self, demandYear, currentPeak):
        
        FESYearlyPeak = Utils.loadTextFile('Generation/NationalGrid_FES_TwoDeg_PeakDemandChange.txt')
        y = demandYear-2010
        newPeakD = FESYearlyPeak[y]*1000000.0
        return newPeakD
    
    # estimare capacity in a specific year
    def estimateCapacityYear(self, capYear, genCompanies):
        totCap = 0.0
        for i in range(len(genCompanies)):
            totCap = totCap + genCompanies[i].getCapYear(capYear,True) # true for derated capacity
        return totCap


    # hold capacity auction
    def capacityAuction(self, timeHorizon, currentPeak, genCompanies, boolEnergyStorage, busheadroom):
        print('---------------------- Capacity Auction Method ---------------------')
        demandYear = self.year+timeHorizon
        scaleACS = 1.09
        # Book: Ter-Gazarian, A.G., Energy Storage for Power Systems, Page 18
        estPeakD = (self.estimateDemandYear(demandYear,currentPeak)* scaleACS)
        estDeRCap = self.estimateCapacityYear(demandYear, genCompanies)
        print('Estimated Peak Demand ', estPeakD)
        print('Estimated Derated Capacity ', estDeRCap)
        
        if(estPeakD>estDeRCap):
            print('---------------------- Holding Capacity Auction ---------------------')
            TECHFILENAME = 'GEN_TYPE_LIST.txt'
            file2 = open(TECHFILENAME, "r") 
            technologyList = file2.read().split('\n')
            file2.close()
            technologyList.pop()

            newCapList = list()
            capShortFall = estPeakD - estDeRCap
            bids = np.zeros((0,8), dtype='object') #0 means title; bids for one company [plants,7domains]
            numBids = 0
            numZeroPriceBids = 0
            zeroPriceBidDeRCapSum = 0.0
            zeroPriceBidCompanyIndx = list()
            randGenCompaniesIndx = Utils.randomOrderListIndx(genCompanies)
            for i in range(len(randGenCompaniesIndx)):
                indx = randGenCompaniesIndx[i]

                bidType, bidPrice, bidCapacity, bidConstructionTime, bidDeRCapacity, batteryBoolList, makeBid, bidbus = genCompanies[indx].getCapAuctionBid(timeHorizon, capShortFall, boolEnergyStorage,busheadroom)
                if(makeBid):
                    numBids = numBids + 1
                    tempBids = np.zeros((len(bidType),8), dtype='object')
                    
                    for j in range(len(bidType)):
                        tempBids[j,0] = bidPrice[j]
                        tempBids[j,1] = bidCapacity[j]
                        tempBids[j,2] = float(indx)
                        tempBids[j,3] = bidType[j]
                        tempBids[j,4] = bidConstructionTime[j]
                        tempBids[j,5] = bidDeRCapacity[j]
                        tempBids[j,6] = batteryBoolList[j]
                        tempBids[j,7] = bidbus[j]
                    bids = np.concatenate((bids,tempBids), axis=0)

            bids = bids[bids[:,0].argsort()] # sort based on price: all companies all plants
            # Loop through bids and allocate cap subsidies until demand is met (include cap of 75£/kW as per BRAIN paper)
            requiredCap = capShortFall

            if(numBids>0): # Getting Cap Auction Strike Price
                count =0
                for i in range (bids.shape[0]): #rows bids number
                    if(requiredCap>0 and bids[i,1]>0):#equalivent to while
                        
                        bidDeratedCap = float(bids[i,5])
                        bidCap = float(bids[i,1])
                        bidSub = float(bids[i,0])
                        if(bidSub>75):
                            bidSub = 75 # 75 GBP/kW capacity
                        requiredCap = requiredCap - bidDeratedCap
                        count = count+1
                        
          #      outputBids = np.zeros((count,8), dtype='object')
                outputBids = np.zeros((0,9), dtype='object')
                requiredCap = capShortFall
                tempCount = 0
                for i in range (bids.shape[0]): 
                    if(requiredCap>0 and float(bids[i,1])>0):
                        TEMPoutputBids = np.zeros((1,9), dtype='object')
                        for k in range(8):
                       #     outputBids[tempCount,k] = bids[i,k]
                            TEMPoutputBids[0,k] = bids[i,k]
                #        outputBids[tempCount,7] = bidSub
                        TEMPoutputBids[0,8] = bidSub # the differencr from bid price is 75
                        outputBids = np.concatenate((outputBids,TEMPoutputBids), axis=0)
                        tempCount = tempCount+1

                        bidDeratedCap = float(bids[i,5])
                        bidCap = float(bids[i,1])
                        bidConstructT = int(bids[i,4])  
                        bidBus = bids[i,7]                      
                        tGenName = bids[i,3]
                        if(int(bids[i,6])==1):
                            batteryBool = True
                        else:
                            batteryBool = False

                        if(not batteryBool):
                            tRenewableID = 0
                            lifetime = genCompanies[0].checkPlantLifeTime(tGenName, False)
                            tCapacityKW = bidCap
                            tStartYear = bidConstructT + self.year
                            tEndYear = tStartYear + lifetime
                            
                            tAge = 0
                            cfdBool = False
                            capMarketBool = True

                            genCompanies[int(round(bids[i,2]))].addToConstructionQueue(tGenName, tRenewableID, tCapacityKW, tStartYear, tEndYear, tAge, bidSub, cfdBool,capMarketBool, bidBus)
                            tempCapList = Utils.addToCapGenList(tGenName, tCapacityKW,newCapList,technologyList)
                            newCapList = tempCapList
                            requiredCap = requiredCap - bidDeratedCap
                        else:
                            genCompanies[int(round(bids[i,2]))].addBatterySizeCapacitySub(bidCap, bidSub)
                            genCompanies[int(round(bids[i,2]))].curYearBatteryBuild += bidCap
                            
                outFileName = 'Results/test/CapacityMarketSuccessfulBidsYear'+str(self.year)+'.csv'
                outBidDF = pd.DataFrame(outputBids)
                outBidDF.columns = ['bidPrice', 'Capacity', 'indx', 'Type', 'ConstructionTime', 'DeRateCap', 'Battery', 'bidBus' ,'STRIKEPriceGBP']
                outBidDF.to_csv(outFileName, index = False)

                            
            Utils.updateCurYearCapInvest(technologyList, newCapList)
        else:
            print(' ----------------- No capacity auction ----------------------')

            
    # method to hold CfD auction
    def cfdAuction(self, capYears, commisCap, genCompanies, busheadroom):
        print('++++++++++++++++++ CfD auction method +++++++++++++++++++++++')
        TECHFILENAME = 'GEN_TYPE_LIST.txt'
        file2 = open(TECHFILENAME, "r") 
        technologyList = file2.read().split('\n')
        file2.close()
        technologyList.pop()
        newCapList = list()
        
        # check if commissioning year
        y = self.year - self.BASEYEAR
        if (y%capYears == 0): #capYears =3
            print('++++++++++++++++++ Holding CfD auction +++++++++++++++++++++++')
            bids = np.zeros((0,6), dtype='object')
            numBids = 0
            randGenCompaniesIndx = Utils.randomOrderListIndx(genCompanies)
            for i in range(len(randGenCompaniesIndx)):
                indx = randGenCompaniesIndx[i]
                bidType, bidPrice, bidCapacity, bidConstructionTime, makeBid, bidbus = genCompanies[indx].getCFDAuctionBid(busheadroom)
                if(makeBid):
                    numBids = numBids + 1
                    tempBids = np.zeros((len(bidType),6), dtype='object')
                    for j in range(len(bidType)):
                        tempBids[j,0] = bidPrice[j]
                        tempBids[j,1] = bidCapacity[j]
                        tempBids[j,2] = float(indx)
                        tempBids[j,3] = bidType[j]
                        tempBids[j,4] = bidConstructionTime[j]
                        tempBids[j,5] = bidbus[j]
                        
                    bids = np.concatenate((bids,tempBids), axis=0)
            bids = bids[bids[:,0].argsort()] # sort based on price

            count = 0
            allocatedCap = 0
            
            if(numBids>0): # Getting Cap Auction Strike Price
                strikePrice = 0.0
                for i in range (bids.shape[0]):#row
                    if(allocatedCap<commisCap and bids[i,1]>0):#commisioned capacity 6GW
                        companyIndx = int(round(bids[i,2]))
                        bidPrice = bids[i,0]
                        bidCap = bids[i,1]
                        bidType = bids[i,3]
                        
                        strikePrice = bidPrice # GBP/kWh
                        allocatedCap = allocatedCap + bidCap
                        count = count+1

                allocatedCap = 0
                self.curCFDPrice = strikePrice

           #     outputBids = np.zeros((count,6), dtype='object')
                outputBids = np.zeros((0,7), dtype='object')
                tempCount = 0
                for i in range (bids.shape[0]): # allocating CfD Subs
                    if(allocatedCap<commisCap and bids[i,1]>0):
                        TEMPoutputBids = np.zeros((1,7), dtype='object')
                        for k in range(6):
                            TEMPoutputBids[0,k] = bids[i,k]
                   #         outputBids[tempCount,k] = bids[i,k]
                  #      outputBids[tempCount,5] = self.curCFDPrice
                        TEMPoutputBids[0,6] = self.curCFDPrice
                        outputBids = np.concatenate((outputBids,TEMPoutputBids), axis=0)
                        tempCount = tempCount +1
                        
                        companyIndx = int(round(bids[i,2]))
                        bidPrice = bids[i,0]
                        bidCap = bids[i,1]
                        bidType = bids[i,3]
                        bidConstructT = bids[i,4]
                        bidBus = bids[i,5]
                        rGenName = bidType
                        if(rGenName=='Nuclear' or rGenName=='BECCS'):
                            rRenewableID = 0
                            lifetime = genCompanies[0].checkPlantLifeTime(rGenName, False)
                        else:
                            rRenewableID = 1
                            lifetime = genCompanies[0].checkPlantLifeTime(rGenName, True)
                        rCapacityKW = bidCap
                        rStartYear = bidConstructT + self.year
                        rEndYear = rStartYear + lifetime
                        rAge = 0
                        cfdBool = True
                        capMarketBool = False
                        genCompanies[companyIndx].addToConstructionQueue(rGenName, rRenewableID, rCapacityKW, rStartYear, rEndYear, rAge, strikePrice, cfdBool, capMarketBool, bidBus)
                        tempCapList = Utils.addToCapGenList(rGenName, rCapacityKW,newCapList,technologyList)
                        newCapList = tempCapList
                        
            outFileName = 'Results/test/CfDMarketSuccessfulBidsYear'+str(self.year)+'.csv'
            outBidDF = pd.DataFrame(outputBids)
            outBidDF.columns = ['bidPrice', 'Capacity', 'indx', 'Type', 'ConstructionTime', 'bidBus','STRIKEPriceGBP/kWh']
            outBidDF.to_csv(outFileName, index = False)
                
            Utils.updateCurYearCapInvest(technologyList, newCapList)
        else:
            print('++++++++++++++++++ No CfD auction +++++++++++++++++++++++')


            

    # old function, not used anywhere
    def increaseCO2Price(self, pcIncrease): # fraction between 0 and 1
        self.curCO2Price = self.curCO2Price*(1+pcIncrease)

    
    def recordYearData(self):
        self.yearlyCO2Price.append(self.curCO2Price)
        self.yearlyCFDPrice.append(self.curCFDPrice)
    
    # graph CO2 price
    def yearGraph(self):
        import matplotlib.pyplot as plt
        y=self.years
        fig, axs = plt.subplots(2,1)
        fig.suptitle(self.name, fontsize=20)
        axs[0].plot(y, self.yearlyCO2Price)
        axs[0].set_ylabel('CO2 Price (GBP/t)')
        axs[1].plot(y, self.yearlyCFDPrice)
        axs[1].set_ylabel('CFD Price (GBP/kWh)')

        from matplotlib.ticker import MaxNLocator
        axs[0].xaxis.set_major_locator(MaxNLocator(integer=True))
        axs[1].xaxis.set_major_locator(MaxNLocator(integer=True))
        
        fig.show()

    # output results to csv
    def writeResultsToFile(self, RESULTS_FILE_PATH):
        fileOut = RESULTS_FILE_PATH + 'YearlyPolicy.csv'

        outNames = list()
        outNames.append('Year')
        outNames.append('Act_CO2Price')
        outNames.append('BEIS_CO2Price')
        outNames.append('CO2Emissions(gCO2/kWh)')
        outNames.append('CO2EmissionsTarget(gCO2/kWh)')

        outData = list()
        outData.append(self.years)
        outData.append(self.yearlyCO2Price)
        outData.append(self.yearlyCarbonCost)
        outData.append(self.yearlyEmissionsIntensity)
        outData.append(self.yearlyEmissTarget)

        Utils.writeListsToCSV(outData,outNames,fileOut)
        






















    







        
        
