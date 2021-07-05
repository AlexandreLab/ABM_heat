import joblib
import random
import numpy as np
from random import choice
import scipy as sp
from scipy import (dot, eye, randn, asarray, array, trace, log, exp, sqrt, mean, sum, argsort, square, arange)
from scipy.stats import multivariate_normal, norm
from scipy.linalg import (det, expm)
from customer import customer
from customerGroup import customerGroup
from renewableGenerator import renewableGenerator
from traditionalGenerator import traditionalGenerator
from energyStorage import energyStorage
from generationCompany import generationCompany
from drawMap import drawMap
from policyMaker import policyMaker
from heatProvider import heatProvider
from drawMap_noGeopy import drawMap as oldDrawMap
import Utils
import random
import pandas as pd 


# method to count number of companies with plants of each technology, e.g. hydro, CCGT, etc.
def countCompaniesPerTech(genCompanies, genTechList):
    genTypeCompanyCount = list()
    for i in range(len(genTechList)):
        genTypeCompanyCount.append(0)
        
    for i in range(len(genCompanies)):
        genTypes, genCap, genTypesNonZero = genCompanies[i].getGenPortfolio()

        for j in range(len(genTypesNonZero)):
            indx = genTechList.index(genTypesNonZero[j])
            genTypeCompanyCount[indx] +=1

    for i in range(len(genTechList)):
        print('%s companies with %s plants '%(str(genTypeCompanyCount[i]),str(genTechList[i])))

    return genTechList, genTypeCompanyCount #e.g. 4 companies with CCGT

# method to get the capacity of each technology, e.g. 4 GW of solar, etc.
def getCapacityPerTech(genCompanies):
    techTypes = list()
    techCap = list()
    techDeRCap = list()

    for i in range(len(genCompanies)):
        indx = len(genCompanies[i].yearlyCapPerTech)-1
        capPerTech = genCompanies[i].yearlyCapPerTech #50 year
        deRCapPerTech = genCompanies[i].yearlyDerateCapPerTech
        techNames = genCompanies[i].techNames

        for j in range(len(techNames)):
            yindx = len(capPerTech[j])-1 #last year

            if(not (techNames[j] in techTypes)):
                techTypes.append(techNames[j])
                techCap.append(capPerTech[j][yindx])
                techDeRCap.append(deRCapPerTech[j][yindx])
            else:
                tIndx = techTypes.index(techNames[j])
                techCap[tIndx] = techCap[tIndx] + capPerTech[j][yindx]
                techDeRCap[tIndx] = techDeRCap[tIndx] + deRCapPerTech[j][yindx]

    for i in range(len(techTypes)):
        print('%s : Cap (MW) = %s : Derated Cap (MW) = %s '%(techTypes[i],str(techCap[i]/1000.0),str(techDeRCap[i]/1000.0)))

#    Utils.graphMultSeriesOnePlot(techCap, 'Year', 'Capacity', 'Annual GB Capacity',techTypes)
#    Utils.graphMultSeriesOnePlot(techDeRCap, 'Year', 'Capacity', 'Annual GB De Rated Capacity',techTypes)

    return techTypes, techCap, techDeRCap
                


# method to plot yearly capacity of each technology
def graphYearlyCapacity(years, yearlyTotCap, yearlyDeRCap, yearlyPeakD, yearlyCapM, yearlyDeRCapM):
    import matplotlib.pyplot as plt

    fig = plt.figure()
    fig.suptitle('Annual Total Capacity Change', fontsize=20)
    ax1 = fig.add_subplot(111)
    y = years # 1,2,3,4 append


    ax1.plot(y,yearlyTotCap)
    ax1.plot(y,yearlyDeRCap)
    ax1.plot(y,yearlyPeakD)
    ax1.plot(y,yearlyCapM)
    ax1.plot(y,yearlyDeRCapM)
    ax1.set_ylabel('kW')
    
    from matplotlib.ticker import MaxNLocator
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.set_xlabel('Year')

    ax1.legend(['TotalCapacity', 'DeRatedCapacity', 'PeakDemand','CapacityMargin','DeRatedCapacityMargin'], loc='upper left')
    fig.show()

# method to plot yearly capacity per bus per tech
def graphYearlyBus(years, yearlycaplist, buslist, techtype):    
    import matplotlib.pyplot as plt

    fig = plt.figure()
    fig.suptitle('Annual Capacity Change of '+techtype, fontsize=20)
    ax1 = fig.add_subplot(111)
    y = years # 1,2,3,4 append
    #given new added bus, add zero to previous position
    b = len(yearlycaplist[-1])
    for j in range(len(yearlycaplist)):
        c = len(yearlycaplist[j])
        yearlycaplist[j] = yearlycaplist[j] + [0]*(b-c)
    #transpose the dimension of bus and year
    a=np.array(yearlycaplist)
    a = a.transpose(1,0)
    yearlycaplist = a.tolist()
    for i in range(len(buslist)):
        ax1.plot(y,yearlycaplist[i])
        ax1.set_ylabel('kWh')
    from matplotlib.ticker import MaxNLocator
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.set_xlabel('Year')
    busname=['bus'+str(i) for i in buslist]
    ax1.legend(busname, loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
    fig.show()    




def graphheadroom(years, yearlyheadroom):
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    headroomarray = np.array(yearlyheadroom)
    fig, ax = plt.subplots(figsize=(7,8))
    im = ax.imshow(headroomarray, aspect='auto')
    bus = list(range(1,31))
    y_axis =  [str(j) for j in years]
    x_axis =  [str(k) for k in bus]

    ax.set_xticks(np.arange(len(x_axis)))
    ax.set_yticks(np.arange(len(y_axis)))
    ax.set_xticklabels(x_axis)
    ax.set_yticklabels(y_axis)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    ax.set_title("Headroom for 30 Busbar")

    fig.tight_layout()
    plt.xlabel('Busbar')
    plt.ylabel('Year')
    plt.colorbar(ax.imshow(-headroomarray, aspect='auto'))
    plt.show()

######### main method, code starts executing from here ##################
if __name__ == '__main__':
    import time
    import statistics as stats
    np.random.seed(42)
    random.seed(42)
    descrip = "---test---"
    print('========================begin======================== ')
    Utils.resetCurYearCapInvest()
    BASEYEAR = 2010 # 2010
    file = open("BASEYEAR.txt", "w") 
    file.write(str(BASEYEAR)) 
    file.close()

    # path to where you want results output to
    RESULTS_FILE_PATH = 'Results/test/'

    maxYears = 5 #16 = 2025 #9=2018 #  25 = 2034, 41 = 2050
    timeSteps=8760
    boolDrawMap = False
    boolDrawYearlyCompanies = False
    boolDrawYearlyCap = True
    boolDrawPolicyGraph = True
    boolDrawDemandGenGraph = False
    boolDrawGenMixGraph = True
    boolDrawCurYearRenGen = False

    boolEnergyStorage = True
    boolLinearBatteryGrowth = False

    # these battery capacity values are only needed if a linear increase in battery is implemented
    if(BASEYEAR == 2018):
        totalBatteryCap = 700000.0 # 700 MW in 2018
    elif(BASEYEAR == 2010):
        totalBatteryCap = 0.0 #10000.0 # 10 MW in 2010????
  #      totalBatteryCap = 22512000.0 #10000.0 # 10 MW in 2010????

    # FES Two Degrees scenario says 3.59 GW batteries in 2018 and 22.512 GW in 2050
    # http://fes.nationalgrid.com/media/1409/fes-2019.pdf page 133
        
    totalFinalBatteryCap = 22512000.0 #10000000.0 # 10 GW in 2050
 #   totalFinalBatteryCap = 10000000.0 # 10 GW in 2050
    totalStartBatteryCap = totalBatteryCap

    years = list()
    yearlyTotCap = list()
    yearlyDeRCap = list()
    yearlyPeakD = list()
    yearlyCapM = list()
    yearlyDeRCapM = list()
    yearlyheadroom = list()
    policy = policyMaker()

    energyCustomers = list()

    techTypes = list()
    techCapYear = list()
    techDeRCapYear = list()


    #for accounting basbar per tech
    nuclearbuslist = list()
    yearlynuclearcaplist = list()      
    coalbuslist = list()
    yearlycoalcaplist = list()      
    windoffbuslist = list()
    yearlywindoffcaplist = list()
    beccsbuslist = list()
    yearlybeccscaplist = list()    
    # If you want to break down the customers by region, use this code
    '''
    cust = customerGroup(3147588, 0.00, 1, 'London') 
    energyCustomers.append(cust)
    cust = customerGroup(2466175, 0.00, 2, 'Scotland') 
    energyCustomers.append(cust)
    cust = customerGroup(3617257, 0.00, 3, 'South East') 
    energyCustomers.append(cust)
    cust = customerGroup(3109317, 0.00, 4, 'North West') 
    energyCustomers.append(cust)
    cust = customerGroup(1945382, 0.00, 5, 'East Midlands') 
    energyCustomers.append(cust)
    cust = customerGroup(2495526, 0.00, 6, 'East England') 
    energyCustomers.append(cust)
    cust = customerGroup(2291848, 0.00, 7, 'Yorkshire') 
    energyCustomers.append(cust)
    cust = customerGroup(2324274, 0.00, 8, 'South West') 
    energyCustomers.append(cust)
    cust = customerGroup(2348914, 0.00, 9, 'West Midlands') 
    energyCustomers.append(cust)
    cust = customerGroup(1349610, 0.00, 10, 'Wales') 
    energyCustomers.append(cust)
    cust = customerGroup(1168992, 0.00, 11, 'North East') 
    energyCustomers.append(cust)
    cust = customerGroup(0, 0.00, 12, 'Non-Residential') 
    energyCustomers.append(cust)
    
    '''

    # if you want to use 1 customer for all GB, use this code
    #cust = customerGroup(0, 0.00, 13, 'All GB Consumers') 
  
    for c in range(1,31):
        cust = customerGroup(c)
        energyCustomers.append(cust)

    # list of generation technologies
    genTechList = list()
    genTechList.append('CCGT')
    genTechList.append('OCGT')
    genTechList.append('Coal')
    genTechList.append('Nuclear')
    genTechList.append('Wind Offshore')
    genTechList.append('Wind Onshore')
    genTechList.append('Solar')
    genTechList.append('Hydro')
    genTechList.append('Biomass')
    genTechList.append('BECCS')

    file = open("GEN_TYPE_LIST.txt", "w")
    for i in range(len(genTechList)):
        temp = str(genTechList[i])+'\n'
        file.write(temp)
    file.close()

    file = open("GEN_TYPE_COMPANY_COUNT_LIST.txt", "w")
    for i in range(len(genTechList)):
        temp = str(1)+'\n'
        file.write(temp)
    file.close()


    # --------- Create generation companies -----------------
    print('Adding Generation Companies')
    elecGenCompanies = list()
    elecGenCompNAMESONLY = list()
    if(BASEYEAR==2018):
        mainPlantsOwnersFile = 'OtherDocuments/UKPowerPlans2018_Owners2.csv'
    elif(BASEYEAR==2010):
        mainPlantsOwnersFile = 'OtherDocuments/UKPowerPlans2010_Owners.csv'
    GBGenPlantsOwners = Utils.readCSV(mainPlantsOwnersFile)

    for i in range(len(GBGenPlantsOwners['Station Name'])):
        tempName = GBGenPlantsOwners['Fuel'].iloc[i] #raw
        
        if(not (GBGenPlantsOwners['Location'].iloc[i]== 'Northern Ireland')and tempName in genTechList):
            curCompName = GBGenPlantsOwners['Company Name'].iloc[i]
            if(not (curCompName in elecGenCompNAMESONLY)):
                print(curCompName)
                elecGenCompNAMESONLY.append(curCompName)
                genCompany = generationCompany(timeSteps)
                genCompany.name = curCompName        
                genCompany.removeGeneration()
                elecGenCompanies.append(genCompany)
            

    # -----------------------------------------------------

    # --------- Add plants for main companies -------------
    
    solarCapMW = 0.0
    windOnshoreCapMW = 0.0
    windOffshoreCapMW = 0.0
    biomassCapMW = 0.0
    print('Adding Plants')
    totCoalSubs = 15000000 # 15GW of cap market subs for coal
    curCoalSub = 0
    for i in range(len(GBGenPlantsOwners['Station Name'])): # data from 2018 dukes report
        tempName = GBGenPlantsOwners['Fuel'].iloc[i]
        
        if(not (GBGenPlantsOwners['Location'].iloc[i]== 'Northern Ireland') and tempName in genTechList):
            curCompName = GBGenPlantsOwners['Company Name'].iloc[i]
            for j in range(len(elecGenCompanies)):
                if(elecGenCompanies[j].name == curCompName):
                    tempName = GBGenPlantsOwners['Fuel'].iloc[i]
                    tempTypeID = -1
                    lifetime = 0
                    tempRen = 0
                    tempCapKW = GBGenPlantsOwners['Installed Capacity(MW)'].iloc[i]*1000.0
                    tempbus = GBGenPlantsOwners['Bus'].iloc[i]
                    if(tempName=='Nuclear'):
                        lifetime = 60
                        tempRen = 0
                        #if(not tempbus in [5,7,10,11,20,27]):
                            #tempCapKW = 0
                    elif(tempName=='CCGT'):
                        lifetime = 25
                        tempRen = 0
                    elif(tempName=='OCGT'):
                        lifetime = 25
                        tempRen = 0
                    elif(tempName=='Coal'):
                        lifetime = 25
                        tempRen = 0
                        if(curCoalSub<totCoalSubs):
                            coalCapSub = 75
                            curCoalSub = curCoalSub + tempCapKW
                            coalCapMarketBool = True
                        else:
                            coalCapSub = 0
                            coalCapMarketBool = False
                        #if(not tempbus in [4,11,15,16,18]):
                            #tempCapKW = 0
                    elif(tempName=='BECCS'):
                        lifetime = 25
                        tempRen = 0
                    elif(tempName=='Wind Offshore'):
                        lifetime = 22
                        tempRen = 1
                        #if(not tempbus in [1,2,7,8,9,10,11,12,13,15,16,19,20,26,27,28,29]):
                            #tempCapKW = 0  
                        windOffshoreCapMW = windOffshoreCapMW + tempCapKW/1000.0

                        renGen = renewableGenerator(5,8760, tempCapKW,0.0,1) # temporary generator to estimate the annual costs
                        yearCost, yCostPerKWh = renGen.estAnnualCosts(tempCapKW)
                      
                    elif(tempName=='Wind Onshore' or tempName=='Wind'):
                        tempName = 'Wind Onshore'
                        lifetime = 24
                        tempRen = 1
                        windOnshoreCapMW = windOnshoreCapMW + tempCapKW/1000.0
                    elif(tempName=='Solar'):
                        lifetime = 25
                        tempRen = 1
                        solarCapMW = solarCapMW + tempCapKW/1000.0
                    elif(tempName=='Hydro'):
                        lifetime = 41
                        tempRen = 1
                       # if(not tempbus in [1,12]):
                          #  tempCapKW = 0  
                    elif(tempName=='Biomass'):
                        lifetime = 25
                        tempRen = 1
                        biomassCapMW = biomassCapMW + tempCapKW/1000.0

                        
                    tempStartYear = int(GBGenPlantsOwners['StartYear'].iloc[i])
                    tempEndYear = tempStartYear + lifetime
                    if(tempEndYear<BASEYEAR):
                        tempEndYear = random.randint(2018, 2025)

                    tempAge = tempStartYear - BASEYEAR
                    if(tempName=='Wind Offshore'):
                  #      elecGenCompanies[j].addGeneration(tempName, tempTypeID, tempRen, tempCapKW, tempStartYear, tempEndYear, tempAge, coalCapSub, False, coalCapMarketBool)
                        elecGenCompanies[j].addGeneration(tempName, tempTypeID, tempRen, tempCapKW, tempStartYear, tempEndYear, tempAge, yCostPerKWh, True, False, tempbus)
                    else:
                        elecGenCompanies[j].addGeneration(tempName, tempTypeID, tempRen, tempCapKW, tempStartYear, tempEndYear, tempAge, 0.0, False, False, tempbus)

    # --------------------------------------------------------------------------

    # --------- Add generation from smaller distributed generation -------------
    
    distGenCompany = generationCompany(timeSteps)
    distGenCompany.name = 'Distributed Generation'
    distGenCompany.removeGeneration()
    
    
#    solarCapMW2018 = 8200 # actual 2018 capacities from BEIS Report
    solarCapMW2018 = 13000 # actual 2018 capacities from BEIS Report
    windOnshoreCapMW2018 = 12100 # actual 2018 capacities from BEIS Report
    windOffshoreCapMW2018 = 8700 # actual 2018 capacities from BEIS Report
    biomassCapMW2018 = 4800 # actual 2018 capacities from BEIS Report
    # No need for hydro here, hydro is accurately included in DUKES report
    

    solarCapMW2010 = 111 # actual 2010 capacities from BEIS Report
    windOnshoreCapMW2010 = 5564
    # actual 2010 capacities from https://www.statista.com/statistics/240178/uk-onshore-wind-power-capacity/
    windOffshoreCapMW2010 = 1341.2
    # actual 2010 capacities from http://www.ewea.org/fileadmin/files/library/publications/statistics/20110121_Offshore_stats_Full_Doc_final.pdf
#    biomassCapMW2018 = 4800 # actual 2018 capacities from BEIS Report
    # No need for hydro here, hydro is accurately included in DUKES report



    pvPlantsFile = 'OtherDocuments/OperationalPVs2017test_wOwner.csv' # these records are for end of 2017
    GBPVPlants = Utils.readCSV(pvPlantsFile)
    
    biomassPlantsFile = 'OtherDocuments/OperationalBiomass2017test_wOwner.csv'
    GBBiomassPlants = Utils.readCSV(biomassPlantsFile)
    
    windOnPlantsFile = 'OtherDocuments/OperationalWindOnshore2017test_wOwner.csv'
    GBWindOnPlants = Utils.readCSV(windOnPlantsFile)
    
    windOffPlantsFile = 'OtherDocuments/OperationalWindOffshore2017test_wOwner.csv'
    GBWindOffPlants = Utils.readCSV(windOffPlantsFile)
    print('Adding Additional Distributed Generation')


    if(BASEYEAR==2018):
        avgPVStartYear = int(round(GBPVPlants['StartYear'].mean()))
        avgBiomassStartYear = int(round(GBBiomassPlants['StartYear'].mean()))
        avgWindOnStartYear = int(round(GBWindOnPlants['StartYear'].mean()))
        avgWindOffStartYear =int(round(GBWindOffPlants['StartYear'].mean()))
    else:
        avgPVStartYear = BASEYEAR - 1
        avgBiomassStartYear = BASEYEAR - 1
        avgWindOnStartYear = BASEYEAR - 1
        avgWindOffStartYear = BASEYEAR - 1
    
    print('avgPVStartYear ',avgPVStartYear)
    print('avgBiomassStartYear ',avgBiomassStartYear)
    print('avgWindOnStartYear ',avgWindOnStartYear)
    print('avgWindOffStartYear ',avgWindOffStartYear)

    if(BASEYEAR==2018):
        sCapkW = (solarCapMW2018 - solarCapMW)*1000.0
        wOnCapkW = (windOnshoreCapMW2018 - windOnshoreCapMW)*1000.0
        wOffCapkW = (windOffshoreCapMW2018 - windOffshoreCapMW)*1000.0  #actual data- recod large plant=distributed
    elif(BASEYEAR==2010):
        sCapkW = (solarCapMW2010 - solarCapMW)*1000.0
        wOnCapkW = (windOnshoreCapMW2010 - windOnshoreCapMW)*1000.0
        wOffCapkW = (windOffshoreCapMW2010 - windOffshoreCapMW)*1000.0

        for i in range(len(GBWindOffPlants['Name'])): # Adding in offshore plants already under construction that are due to come online soon
            sYear = GBWindOffPlants['StartYear'].iloc[i]
            if(sYear>2010 and sYear<2014):
                tempName = GBWindOffPlants['Type'].iloc[i]
                cap = GBWindOffPlants['Capacity(kW)'].iloc[i]
                eYear = GBWindOffPlants['EndYear'].iloc[i]
                tempbus = GBWindOffPlants['Bus'].iloc[i]
                lifetime = eYear - sYear
                renGen = renewableGenerator(5,8760, cap,0.0, tempbus) # temporary generator to estimate the annual costs
                yearCost, yCostPerKWh = renGen.estAnnualCosts(cap)
                if(tempCapKW==183600):
                    print('Wind offshore')
                    print('yearCost ',yearCost)
                    print('2 ')
                    input('wait')
                distGenCompany.addGeneration('Wind Offshore', -1, 1, cap, sYear, 2052, 0, yearCost, True, False, tempbus)
                
        for i in range(len(GBWindOnPlants['Name'])): # Adding in onshore plants already under construction that are due to come online soon
            sYear = GBWindOnPlants['StartYear'].iloc[i]
            if(sYear>2010 and sYear<2013):
                tempName = GBWindOnPlants['Type'].iloc[i]
                cap = GBWindOnPlants['Capacity(kW)'].iloc[i]
                eYear = GBWindOnPlants['EndYear'].iloc[i]
                tempbus = GBWindOnPlants['Bus'].iloc[i]
                lifetime = eYear - sYear
                distGenCompany.addGeneration('Wind Onshore', -1, 1, cap, sYear, eYear, 0, 0.0, False, False, tempbus)

        for i in range(len(GBBiomassPlants['Name'])): # Adding in biomass plants already under construction that are due to come online soon
            sYear = GBBiomassPlants['StartYear'].iloc[i]
            if(sYear>2010 and sYear<2013):
                tempName = GBBiomassPlants['Type'].iloc[i]
                cap = GBBiomassPlants['Capacity(kW)'].iloc[i]
                eYear = GBBiomassPlants['EndYear'].iloc[i]
                tempbus = GBBiomassPlants['Bus'].iloc[i]
                lifetime = eYear - sYear
                distGenCompany.addGeneration('Biomass', -1, 1, cap, sYear, eYear, 0, 0.0, False, False, tempbus)

        
#distcap= difference+come online soon

        
    print('sCapkW ',sCapkW) # distributed capacity
    print('wOnCapkW ',wOnCapkW)
    print('wOffCapkW ',wOffCapkW)

    distGenCompany.addGeneration('Solar', -1, 1, sCapkW, avgPVStartYear, 2052, (avgPVStartYear-BASEYEAR), 0.0, False, False, random.randint(1,30))

    if(BASEYEAR==2018):
        bioCapkW = (biomassCapMW2018 - biomassCapMW)*1000.0
        distGenCompany.addGeneration('Biomass', -1, 1, bioCapkW, avgBiomassStartYear, 2052, (avgBiomassStartYear-BASEYEAR), 0.0, False, False, random.randint(1,30))
    
    distGenCompany.addGeneration('Wind Onshore', -1, 1, wOnCapkW, avgWindOnStartYear, 2052, (avgWindOnStartYear-BASEYEAR), 0.0, False,  False, random.randint(1,30))
    
    renGen = renewableGenerator(5,8760, wOffCapkW,0.0,1) # temporary generator to estimate the annual costs, for cfd
    yearCost, yCostPerKWh = renGen.estAnnualCosts(wOffCapkW)
    distGenCompany.addGeneration('Wind Offshore', -1, 1, wOffCapkW, avgWindOffStartYear, 2052, (avgWindOffStartYear-BASEYEAR), yearCost, True, False, choice([1,2,7,8,9,10,11,12,13,15,16,19,20,26,27,28,29]))

    elecGenCompanies.append(distGenCompany)


    genTechList, genTypeCompanyCount = countCompaniesPerTech(elecGenCompanies, genTechList)

    file = open("GEN_TYPE_LIST.txt", "w")
    for i in range(len(genTechList)):
        temp = str(genTechList[i])+'\n'
        file.write(temp)
    file.close()

    file = open("GEN_TYPE_COMPANY_COUNT_LIST.txt", "w")
    for i in range(len(genTypeCompanyCount)):
        temp = str(genTypeCompanyCount[i])+'\n'
        file.write(temp)
    file.close()

    for i in range(len(elecGenCompanies)):
        elecGenCompanies[i].updateBuildRates()
        tname1 = elecGenCompanies[i].name
    #    print('company ',i)
        print('name, ',tname1)
  #  input('wait')

    if(boolEnergyStorage):
        batteryCapPerCompany = totalBatteryCap/len(elecGenCompanies)
        for i in range(len(elecGenCompanies)):
            elecGenCompanies[i].removeBatteries()
  #          elecGenCompanies[i].addBatterySize(batteryCapPerCompany)


    annualStorageCap = list()
    

    
    
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # ---------------------------- Simulation begins here ----------------------
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    
    

    heatAndGas = list() # ignore this for now
    gasProv = heatProvider() 
    heatAndGas.append(gasProv)
    demandCoeff = 1.0 # coefficient to scale non residential demand based on price elasticity#how mauch percentage change compared to 2018. e.g. 180%
    hourlyCurtailPerYear = list()
    yearlyCurtailedInstances = list()

    hourlyLossOfLoadPerYear = list()
    yearlyLossOfLoadInstances = list()
    
    for y in range(maxYears): # Loop through years
        hourlyCurtail = list()
        hourlyLossOfLoad = list()

        print('year ',(BASEYEAR+y))
        print('y ',(y))

        #################### Add in some BECCS ###############
        if(BASEYEAR+y == 2019):
            cName = 'Drax Power Ltd'
            BECCSAddBool = False
            for k in range(len(elecGenCompanies)):
                if(elecGenCompanies[k].name == cName):
                    elecGenCompanies[k].addGeneration('BECCS', -1, 0, 500000.0, 2019, 2044, 0, 0.0, False, False, choice([2,7,10,12,13,14,15,16,17,18,19,20,22,23,24,26,28,30]))
                    BECCSAddBool = True
                    print('BECCS added')
            if(not BECCSAddBool):
                input('BECCS not added ******')

        if(boolEnergyStorage):
            totalBatteryKW = 0.0
            for i in range(len(elecGenCompanies)):
                elecGenCompanies[i].setBatteryWholesalePrice()
                totalBatteryKW = totalBatteryKW + elecGenCompanies[i].getBatteryCapKW()
            annualStorageCap.append(totalBatteryKW)
            totalBatteryCap = totalBatteryKW

        for d in range (1): # set to 1 as each customer will simulate 8760 hours (365 days)
            customerNLs = list() #list of a number of customers, each customer has 8760 hour data
            customerHeatLoads = list()
            totalCustDemand = list()
            custTotalDayLoads = list()
            custElecBills = list()

            renewGens = list() #list of hourly generation for each plant
            totalRenewGen = list()
            totalGenProfPath = 'Generation/TotalElectricityGeneration_hourly_2018_kWh.txt'
            totalGenProfile = Utils.loadTextFile(totalGenProfPath)

            
            for c in range (len(energyCustomers)):
                curCustNL, curCustHeat = energyCustomers[c].runSim() # sim energy consumption each hour
          #      energyCustomers[c].graph() # graph each customer, wales, east england, etc.
                customerNLs.append(curCustNL)
                customerHeatLoads.append(curCustHeat)
                custTotalDayLoads.append(energyCustomers[c].totalNLDemand)
                custElecBills.append(energyCustomers[c].elecCost)

            # --------------- Heat Demand -----------------
            # again, ignore this section for now
            totalHourlyHeadDemand = list()
            # Get total hourly heat demand for all customers
            for h in range(len(customerHeatLoads[0])):
                hourSum = 0.0
                for c in range(len(customerHeatLoads)):
                    hourSum = hourSum + customerHeatLoads[c][h]
                totalHourlyHeadDemand.append(hourSum)
            tempHeatD = totalHourlyHeadDemand.copy()
            # get heat and gas providers to meet demand
            for c in range(len(heatAndGas)):
                curHeatGen,newHeatD = heatAndGas[c].getGeneration(tempHeatD)
        #        heatAndGas[c].graph()
                tempHeatD = list()
                tempHeatD=newHeatD
            #----------------------------------------------


            #------------- get total customer electricity demand -------------
            for c in range (len(customerNLs[0])): # loop through hours 8760hours one year
                sumNL= 0.0
                for i in range (len(customerNLs)): # loop through customers
                    sumNL = sumNL + customerNLs[i][c]
                totalCustDemand.append(sumNL)

            peakDemand = max(totalCustDemand)

            # ----------------------------------------------------------------

                  

            '''
            sumRes = sum(totalCustDemand)
            sumNonRes = sum(nonResidentialDemand)
            sumTotGen = sum(totalGenProfile)
            print('sumRes    ',sumRes)
            print('sumNonRes ',sumNonRes)
            print('sumTotGen ',sumTotGen)
            prof = list()
            prof.append(totalCustDemand)
            prof.append(nonResidentialDemand)
            prof.append(totalGenProfile)
            profN = list()
            profN.append('totalCustDemand')
            profN.append('nonResidentialDemand')
            profN.append('totalGenProfile')

            print('profN ',profN)
            print('prof ',prof)
            
            Utils.writeToCSV(prof,profN,'Results/test/demand.csv')
            '''

            #-------------------------------------------------------------------------
            

            # ---------------- get renewable generation --------------------

            yearGenPerCompanyData = list() #yearly generation, for each type, total generated by all companies all types
            yearGenPerCompanyName = list() #renewable technology list. name is not proper
            rGenType = list()

            allRGenPerCompany = list() # list of total hourly renewable generation all year           
            allRGenPerTechnology = list() # 5 technologies, each has a list ,contain 8760 hourly generation summed by all plants
            # 3D list, number of renewable types -> number of plants per type -> number of hours, e.g. 2 types, 40 plants, 8760 h 
            tempAllRGenPerTechnology = list() #one tech has a list, apended by each plant's 8760
            totYearRGenKWh = 0.0
            
            for gc in range (len(elecGenCompanies)):
                # rGenProf = list of 8760 lists of rGen, e.g. 40 lists for 40 plants
                # yGenPerTechData = list of sum yearly energy gen per plant, e.g. 40 floats
                # yGenPerTechLabels = list of names of each plant type, e.g., Onshore, Onshore, Offshore, Offshore,...
                # tempTotRGEN = list of 8760 vals for total rGen from company
                rGenProf, yGenPerTechData, yGenPerTechLabels, tempTotRGEN = elecGenCompanies[gc].getRenewableGen()
                allRGenPerCompany.append(tempTotRGEN) #list of every company, total generation per per company's 8760 (sum all its plant)
                tempRGens = list()

                for rg in range(len(rGenProf)): #loops through plants
                    renewGens.append(rGenProf[rg])
                    totYearRGenKWh = totYearRGenKWh + elecGenCompanies[gc].renewableGen[rg].yearlyEnergyGen

                    if(gc==0): #initialise the list
                        recorded = False
                        for i in range(len(rGenType)): #1,2,3,4,5
                            if(elecGenCompanies[gc].renewableGen[rg].renewableType == rGenType[i]):
                                recorded = True
                                yearGenPerCompanyData[i] = yearGenPerCompanyData[i] + elecGenCompanies[gc].renewableGen[rg].yearlyEnergyGen
                                tempAllRGenPerTechnology[i].append(rGenProf[rg])
                        if(not recorded):
                            yearGenPerCompanyData.append(elecGenCompanies[gc].renewableGen[rg].yearlyEnergyGen)
                            yearGenPerCompanyName.append(elecGenCompanies[gc].renewableGen[rg].name) #solar, wind
                            rGenType.append(elecGenCompanies[gc].renewableGen[rg].renewableType) #1,2,3,4,5
                            tempRGens = list()
                            tempRGens.append(rGenProf[rg])
                            tempAllRGenPerTechnology.append(tempRGens)

                    else:
                        recorded = False #since the initial company not necessarily has all technology
                        for i in range(len(rGenType)):
                            if(elecGenCompanies[gc].renewableGen[rg].renewableType == rGenType[i]):
                                recorded = True
                                yearGenPerCompanyData[i] = yearGenPerCompanyData[i] + elecGenCompanies[gc].renewableGen[rg].yearlyEnergyGen
                                tempAllRGenPerTechnology[i].append(rGenProf[rg])

                        if(not recorded):
                            yearGenPerCompanyData.append(elecGenCompanies[gc].renewableGen[rg].yearlyEnergyGen)
                            yearGenPerCompanyName.append(elecGenCompanies[gc].renewableGen[rg].name)
                            rGenType.append(elecGenCompanies[gc].renewableGen[rg].renewableType)
                            tempRGens = list()
                            tempRGens.append(rGenProf[rg])
                            tempAllRGenPerTechnology.append(tempRGens)


            for tg in range (len(tempAllRGenPerTechnology)): # loop through technologies , e.g. solar, onshore
                tList = tempAllRGenPerTechnology[tg][0] # is plant number, returns 8760 vals
                for rg in range(len(tempAllRGenPerTechnology[tg])): # loop through plants
                    tList = [x + y for x, y in zip(tList, tempAllRGenPerTechnology[tg][rg])] #parallal loops each technology's total 8760
                allRGenPerTechnology.append(tList)

            for h in range(len(allRGenPerCompany[0])): #8760
                curTot = 0.0
                for gc in range(len(allRGenPerCompany)): #loops through companies
                    curTot = curTot + allRGenPerCompany[gc][h]
                totalRenewGen.append(curTot) # get total renew gen across all companies hourly, apended each hour's value

            rGenNames = yearGenPerCompanyName.copy()
            # --------------------------------------------------------------
            # ------------------- Graph renewable generation ---------------
            if(boolDrawCurYearRenGen):
                rgGraphData = list()
                rgXlab = list()
                rgYlab = list()
                rgSubtitles = list()
                for rg in range (len(allRGenPerTechnology)): #5 tech
                    graphGen,genUnit = Utils.checkUnits(allRGenPerTechnology[rg])
                    rgGraphData.append(graphGen)
                    rgXlab.append('Hour in Year')
                    rgYlab.append('Generated ('+genUnit+')')
                    rgSubtitles.append(yearGenPerCompanyName[rg]) 
                tempTitle = 'Renewable Generation: '+str(BASEYEAR+y)
                    
                Utils.graph(rgGraphData,rgXlab, rgYlab, tempTitle, rgSubtitles)
            # --------------------------------------------------------------


            # Get electricty demand left for traditional generators to meet
            ############## subtract renewables from demand ###########
            
            netDemand = totalCustDemand.copy()  #total consumption of all consumers, 8760 hour 
            netDemand = [x - y for x, y in zip(netDemand, totalRenewGen)]
            for d in range(len(netDemand)):
                if(netDemand[d]<0.0):
                    hourlyCurtail.append(abs(netDemand[d])) #generation>demand
                    netDemand[d]=0.0
                else:
                    hourlyCurtail.append(0.0)
                    
            #########################################################


            #======= subtract BECCS and nuclear from net demand before battery charge/discharge ====
            #=======================================================================================
            

            tradGenTypes = list()
            tradGenTypes.append(4) # BECCS
            tradGenTypes.append(2) # Nuclear

            tradGenNames= list()
            tradGenNames.append('BECCS')
            tradGenNames.append('Nuclear')

            tradGenPerTech= list() # yearly total generation from each tech of traditional generation
            randGenCompaniesIndx = Utils.randomOrderListIndx(elecGenCompanies)
            totYearTGenKWh = 0.0
            allTGenPerTechnology = list() # 5 technologies, each has a list ,contain 8760 hourly generation summed by all plants
            tempNetD = netDemand.copy()

            # ------------------------------------------- Dispatch traditional generators to meet net demand ----------------------------
            for gt in range(len(tradGenTypes)): # for now only have BECCS and nuclear
                tempSum=0.0

                deRCapSum =0.0
                capSum = 0.0
                tempCurTGen = list()
                for i in range(len(elecGenCompanies)): #all companies have been added at the beginning
                    curCap, curDeRCap = elecGenCompanies[i].getCapacityByType(tradGenTypes[gt],False) # a value, total capacity of a tech, a company, summed by all plants 
                    deRCapSum = deRCapSum + curDeRCap
                    capSum = capSum + curCap #a value, total capacity of a tech, summed by all companies
                
                if(max(tempNetD)>deRCapSum): # that means all companies with these types can be added
                    for gc in range(len(randGenCompaniesIndx)):
                        cIndx = randGenCompaniesIndx[gc]
                        sGen, newNetD, excessGen, hourGenProf = elecGenCompanies[cIndx].getTraditionalGenerationByType(tradGenTypes[gt], tempNetD) #hear, only add company with BECCS and nuclear
                        #sGen is a value sum one year, others are 8760 lists 
                        #in this case newNetD>0, no excessGen
                        tempSum = tempSum + sGen
                        tempNetD = list()
                        tempNetD = newNetD
                        totYearTGenKWh = totYearTGenKWh + sGen
                        if(len(tempCurTGen)==0):
                            tempCurTGen = hourGenProf.copy()
                        else:
                            for k in range(len(tempCurTGen)):
                                val = tempCurTGen[k]
                                tempCurTGen[k] = val + hourGenProf[k] #sum for each tech, total gen from all companies

                                
                        if(sum(excessGen)>0):
                            for k in range(len(hourlyCurtail)):
                                hourlyCurtail[k] = hourlyCurtail[k] + excessGen[k]
                    tradGenPerTech.append(tempSum)
                    
                else:
                    prevTempNetD = tempNetD.copy()
                    curS = 0.0
                    for gc in range(len(randGenCompaniesIndx)):
                        cIndx = randGenCompaniesIndx[gc]
                        curCap, curDeRCap = elecGenCompanies[cIndx].getCapacityByType(tradGenTypes[gt],False)
                        if(capSum>1): # need to make sure not dividing by 0 , for noe, other types,e.g. coal CCGT is zero
                            capFrac = curCap/capSum 
                        else:
                            capFrac = 0.0

                        curTempNetD = prevTempNetD.copy()    
                        curNetD = [x*capFrac for x in curTempNetD]
                        # since netdemand<generation capacity, it will be afforded by caoacity share of each compane, the excess gen will be curtailed
                        sGen, newNetD, excessGen, hourGenProf = elecGenCompanies[cIndx].getTraditionalGenerationByType(tradGenTypes[gt], curNetD)
                        tempSum = tempSum + sGen
                        curS = curS + sGen # total year generation per tech by all companies
                        totYearTGenKWh = totYearTGenKWh + sGen
                        
                        if(len(tempCurTGen)==0):
                            tempCurTGen = hourGenProf.copy()
                        else:
                            for k in range(len(tempCurTGen)):
                                val = tempCurTGen[k]
                                tempCurTGen[k] = val + hourGenProf[k]


                        if(sum(excessGen)>0):
                            for k in range(len(hourlyCurtail)):
                                hourlyCurtail[k] = hourlyCurtail[k] + excessGen[k]
                    tradGenPerTech.append(tempSum)
                    if(abs(curS-sum(prevTempNetD))<1):
                        tempNetD = [0.0 for x in prevTempNetD]
                    else:
                        print('curS ', curS)
                        print('sum(prevTempNetD0 ', sum(prevTempNetD))
                        input('problem, these should be equal ....')
                    
                allTGenPerTechnology.append(tempCurTGen)
                for i in range(len(netDemand)):
                    netDemand[i] = netDemand[i] - tempCurTGen[i]
                    
                for d in range(len(netDemand)):
                    if(netDemand[d]<0.0):
                        hourlyCurtail[d] = hourlyCurtail[d] + abs(netDemand[d])
                        netDemand[d]=0.0

            
            #=======================================================================================


            

            # --------- check if battery considered, if it is, charge/discharge accordingly ----------
            # ----------------------------------------------------------------------------------------
            
            if(boolEnergyStorage):
                tNetDemand = netDemand.copy()
                for i in range(len(elecGenCompanies)):
                    newNet = elecGenCompanies[i].chargeDischargeBatteryTime(tNetDemand)
                    tNetDemand = newNet.copy()
                tempNetD = tNetDemand.copy() # final net demand after account for all companies
                batteryProf = list()
                for k in range(len(tempNetD)):#loop through hour
                    val = netDemand[k] - tempNetD[k]
                    batteryProf.append(val)

                # graph first and final years
                if((y==0 or y==maxYears-1)):
                    graphProf = list()
                    graphProf.append(totalCustDemand)# GB electricity demand
                    graphProf.append(netDemand) # demand - renewables - BECCS-Nuclear
                    graphProf.append(tempNetD) # demand - renewables -BECCS-Nuclear - battery

                    maxPeak = max(totalCustDemand) # peak for total demand
                    NBPeak = max(netDemand) # peak for net demand (demand - renewables- BECCS-Nuclear) without battery
                    BPeak = max(tempNetD) # peak for net demand (demand - renewables - BECCS-Nuclear- battery) with battery
                    maxPeakList = list()
                    NBPeakList = list()
                    BPeakList = list()
                    for i in range(len(netDemand)):#8760 hr have the same value, straght line indicates peak
                        NBPeakList.append(NBPeak)
                        BPeakList.append(BPeak)
                        maxPeakList.append(maxPeak)
                        
                    graphProf.append(maxPeakList)
                    graphProf.append(NBPeakList)
                    graphProf.append(BPeakList)

                    
                    graphNames = list()
                    graphNames.append('GB Electricity Demand')
                    graphNames.append('Demand - Renewables')
                    graphNames.append('Demand - Renewables - Battery')
                    p1 = round((maxPeak/1000000),2)
                    p2 = round((NBPeak/1000000),2)
                    p3 = round((BPeak/1000000),2)
                    peak1 = 'Peak: '+str(p1)+' GW'
                    graphNames.append(peak1)
                    peak2 = 'Peak - Renewables: '+str(p2)+' GW'
                    graphNames.append(peak2)
                    peak3 = 'Peak - Renewables - Battery: '+str(p3)+' GW'
                    graphNames.append(peak3)
                    graphT = 'Battery vs No Battery '+str(y+BASEYEAR)+', Battery Capacity: '+str(totalBatteryCap/1000000)+' GW'
                    Utils.graphMultSeriesOnePlotV3(graphProf, 'Hour', 'Electricity Demand', graphT, graphNames)

                    graphProf.append(batteryProf)
                    graphNames.append('Battery Charge/Discharge')
                    
                    fileOut = RESULTS_FILE_PATH + 'BatteryPeakYear'+str(y+BASEYEAR)+'.csv'
                    Utils.writeListsToCSV(graphProf,graphNames,fileOut)


            else: # otherwise, no battery considered
                tempNetD = netDemand.copy()

            for k in range(len(tempNetD)):
                if(tempNetD[d]<0.0):
                    tempV = hourlyCurtail[k]
                    hourlyCurtail[k] = tempV + abs(tempNetD[d])
                    tempNetD[d]=0.0
                    
            # ----------------------------------------------------------------------------------------
                  


            # This is the dispatch order for traditional generation technologies
            tradGenTypes = list()# at this clear the list with BECCS and nuclear
   #         tradGenTypes.append(4) # BECCS         #
   #         tradGenTypes.append(2) # Nuclear       #
            tradGenTypes.append(1) # CCGT
            tradGenTypes.append(0) # Coal
            tradGenTypes.append(3) # OCGT
            
            tradGenNames= list()
   #         tradGenNames.append('BECCS')           #
   #         tradGenNames.append('Nuclear')         #
            tradGenNames.append('CCGT')
            tradGenNames.append('Coal')
            tradGenNames.append('OCGT')


    #        tradGenPerTech= list()                 #
            randGenCompaniesIndx = Utils.randomOrderListIndx(elecGenCompanies)
   #         totYearTGenKWh = 0.0                   #
   #         allTGenPerTechnology = list()          #

            # ------------------------------------------- Dispatch traditional generators to meet net demand ----------------------------
            for gt in range(len(tradGenTypes)):
                tempSum=0.0

                deRCapSum =0.0
                capSum = 0.0
                tempCurTGen = list()
                for i in range(len(elecGenCompanies)):
                    curCap, curDeRCap = elecGenCompanies[i].getCapacityByType(tradGenTypes[gt],False)
                    deRCapSum = deRCapSum + curDeRCap
                    capSum = capSum + curCap
                
                if(max(tempNetD)>deRCapSum):
                    for gc in range(len(randGenCompaniesIndx)):
                        cIndx = randGenCompaniesIndx[gc]
                        sGen, newNetD, excessGen, hourGenProf = elecGenCompanies[cIndx].getTraditionalGenerationByType(tradGenTypes[gt], tempNetD)
                        tempSum = tempSum + sGen
                        tempNetD = list()
                        tempNetD = newNetD
                        totYearTGenKWh = totYearTGenKWh + sGen
                        if(len(tempCurTGen)==0):
                            tempCurTGen = hourGenProf.copy()
                        else:
                            for k in range(len(tempCurTGen)):
                                val = tempCurTGen[k]
                                tempCurTGen[k] = val + hourGenProf[k]

                                
                        if(sum(excessGen)>0):
                            for k in range(len(hourlyCurtail)):
                                hourlyCurtail[k] = hourlyCurtail[k] + excessGen[k]
                    tradGenPerTech.append(tempSum)
                    
                else:
                    prevTempNetD = tempNetD.copy()
                    curS = 0.0
                    for gc in range(len(randGenCompaniesIndx)):
                        cIndx = randGenCompaniesIndx[gc]
                        curCap, curDeRCap = elecGenCompanies[cIndx].getCapacityByType(tradGenTypes[gt],False)
                        if(capSum>1): # need to make sure not dividing by 0 
                            capFrac = curCap/capSum
                        else:
                            capFrac = 0.0

                        curTempNetD = prevTempNetD.copy()    
                        curNetD = [x*capFrac for x in curTempNetD]
                        
                        sGen, newNetD, excessGen, hourGenProf = elecGenCompanies[cIndx].getTraditionalGenerationByType(tradGenTypes[gt], curNetD)
                        tempSum = tempSum + sGen
                        curS = curS + sGen
                        totYearTGenKWh = totYearTGenKWh + sGen
                        
                        if(len(tempCurTGen)==0):
                            tempCurTGen = hourGenProf.copy()
                        else:
                            for k in range(len(tempCurTGen)): #technology
                                val = tempCurTGen[k]
                                tempCurTGen[k] = val + hourGenProf[k]


                        if(sum(excessGen)>0):
                            for k in range(len(hourlyCurtail)):
                                hourlyCurtail[k] = hourlyCurtail[k] + excessGen[k]
                    tradGenPerTech.append(tempSum)
                    if(abs(curS-sum(prevTempNetD))<1):
                        tempNetD = [0.0 for x in prevTempNetD]
                    else:
                        print('curS ', curS)
                        print('sum(prevTempNetD0 ', sum(prevTempNetD))
                        input('problem, these should be equal ....')
                    
                allTGenPerTechnology.append(tempCurTGen)

            # calculating wholesale electricity price from marginal cost
            wholesaleEPrice, nuclearMarginalCost = Utils.getWholesaleEPrice(elecGenCompanies)
            boolNegPrice = False
            for k in range(len(wholesaleEPrice)): #8760
                if(totalRenewGen[k]>totalCustDemand[k]):
                    boolNegPrice = True
     #               print('nuclearMarginalCost[k] old ',nuclearMarginalCost[k])
     #               print('wholesaleEPrice[k] old ',wholesaleEPrice[k])
                    wholesaleEPrice[k] = 0 - nuclearMarginalCost[k]
     #               print('wholesaleEPrice[k] new ',wholesaleEPrice[k])
     #       if(boolNegPrice):
     #           input('????? Did wholesale price go negative ?????')
            fileOut = RESULTS_FILE_PATH + 'WholesalePrice'+str(BASEYEAR+y)+'.csv'
            wholesaleList = list()
            wholesaleList.append(wholesaleEPrice)
            yearListTemp = list()
            yearListTemp.append(str(BASEYEAR+y))
            Utils.writeListsToCSV(wholesaleList,yearListTemp,fileOut)

            # update economics of all plants and batteries
            for k in range(len(elecGenCompanies)):
                elecGenCompanies[k].calcRevenue(wholesaleEPrice)

            lossOfLoadC = 0 # energy unserved
            for k in range(len(tempNetD)):
                if(tempNetD[k]>0.001):
                    val = tempNetD[k]
                    hourlyLossOfLoad.append(val)
                    lossOfLoadC+=1
                else:
                    hourlyLossOfLoad.append(0.0)
            hourlyLossOfLoadPerYear.append(hourlyLossOfLoad)
            yearlyLossOfLoadInstances.append(lossOfLoadC)
                    
            

            yearGenPerCompanyDataTemp = list()
            yearGenPerCompanyNameTemp = list()
            hourlyGenPerCompanyDataTemp = list()
            hourlyTotTGen = list()

            plotDemandGenProf = list()
            plotDemandGenProf.append(totalCustDemand)
            plotDemandGenProf.append(totalRenewGen)
            plotDemandGenNames = list()
            plotDemandGenNames.append('totalCustDemand')
            plotDemandGenNames.append('totalRenewGen')

            traditionalYearlyEnergyGen = 0.0
            traditionalYearlyEnergyGenProf = elecGenCompanies[0].traditionalGen[0].energyGenerated.copy() #8760
            
            for gc in range (len(elecGenCompanies)):
                for tg in range (len(elecGenCompanies[gc].traditionalGen)):
                    traditionalYearlyEnergyGen = traditionalYearlyEnergyGen + elecGenCompanies[gc].traditionalGen[tg].yearlyEnergyGen #yearly
                    traditionalYearlyEnergyGenProf = [x + y for x, y in zip(traditionalYearlyEnergyGenProf, elecGenCompanies[gc].traditionalGen[tg].energyGenerated)]
                    
            hourlyTotTGen = traditionalYearlyEnergyGenProf.copy() #8760 from all traditional plants of all companies
            
            plotDemandGenProf.append(hourlyTotTGen)
            plotDemandGenNames.append('hourlyTotTGen')
            
            if((y==0 or y==maxYears-1) and boolDrawDemandGenGraph):
                Utils.graphMultSeriesOnePlot(plotDemandGenProf, 'Hour', 'kW', 'Demand vs Gen '+str(BASEYEAR+y), plotDemandGenNames)

            yearGenPerCompanyData.extend(tradGenPerTech)# yearly total generation per traditional technology
            tradGenNames= list()
            tradGenNames.append('BECCS')
            tradGenNames.append('Nuclear')
            tradGenNames.append('CCGT')
            tradGenNames.append('Coal')
            tradGenNames.append('OCGT')
            yearGenPerCompanyName.extend(tradGenNames)


            operationalDataOut = list()
            operationalNamesOut = list()

            operationalNamesOut.append('Demand')
            operationalDataOut.append(totalCustDemand.copy())
            if(boolEnergyStorage):
                operationalNamesOut.append('Battery')
                operationalDataOut.append(batteryProf.copy())

            for k in range(len(rGenNames)): # solar wind etc.
                operationalNamesOut.append(rGenNames[k])
                operationalDataOut.append(allRGenPerTechnology[k].copy())

            for k in range(len(tradGenNames)):
                operationalNamesOut.append(tradGenNames[k])
                operationalDataOut.append(allTGenPerTechnology[k].copy())

            fileOut = RESULTS_FILE_PATH + 'HourlyOperationYear'+str(BASEYEAR+y)+'.csv'
            Utils.writeListsToCSV(operationalDataOut,operationalNamesOut,fileOut)
            operationalDataOut = list()
            operationalNamesOut = list()

            if(y==0):
                yearlyGenPerCompanyData = list()
                tempYears = list()
                tempYears.append(BASEYEAR)
                for k in range(len(yearGenPerCompanyData)):#yearGenPerCompanyData is the total generation per technology in current year (10 value for 10 tech)
                    tempList = list()
                    tempList.append(yearGenPerCompanyData[k])
                    yearlyGenPerCompanyData.append(tempList)#10 list for 10 tech, each list contain many years
            else:
                tempYears.append(BASEYEAR+y)
                for k in range(len(yearGenPerCompanyData)):
                    yearlyGenPerCompanyData[k].append(yearGenPerCompanyData[k])
                    
            fileOut = RESULTS_FILE_PATH + 'YearlyGeneration.csv'
            if(y==maxYears-1):
                genNamesOut = yearGenPerCompanyName.copy()
                genNamesOut.insert(0,'Year')
                genDataOut = yearlyGenPerCompanyData.copy()
                genDataOut.insert(0,tempYears) #insert serial number of years
                
                Utils.writeListsToCSV(genDataOut,genNamesOut,fileOut)

            print('yearGenPerCompanyName ',yearGenPerCompanyName)
            print('yearGenPerCompanyData ',yearGenPerCompanyData)
            
            #for gc in range (len(elecGenCompanies)):
                #for tg in range (len(elecGenCompanies[gc].traditionalGen)):
                #    traditionalYearlyEnergyGen = traditionalYearlyEnergyGen + elecGenCompanies[gc].traditionalGen[tg].yearlyEnergyGen #yearly
                #    traditionalYearlyEnergyGenProf = [x + y for x, y in zip(traditionalYearlyEnergyGenProf, elecGenCompanies[gc].traditionalGen[tg].energyGenerated)]
                  




            # -------------- Calculate Profit for each suppier ---------------
            # ignore this section for now, not considering suppliers
            totCustBill = list() # hourly total electricity bill from all customers
            
            for i in range(len(custElecBills[0])):
                totHourBill = 0.0
                for j in range(len(custElecBills)):
                    totHourBill = totHourBill + custElecBills[j][i]
                totCustBill.append(totHourBill)
            # ----------------------------------------------------------------

         

            #--------------------- Map results ---------------------------------
            # no point in using this if not considering customers from different regions
            if(boolDrawMap):
                totalDayDemand = 0.0
                maxDayDemand = max(custTotalDayLoads) #custtotaldayloads is the sum of all year for each consumer, for single consumer  maxDayDemand =ustTotalDayLoads
                tempCustTotalDayLoads = custTotalDayLoads.copy()
                del tempCustTotalDayLoads[len(tempCustTotalDayLoads)-1]
                maxResDayDemand = max(tempCustTotalDayLoads)
                for i in range (len(custTotalDayLoads)):#all consumers
                    totalDayDemand = totalDayDemand + custTotalDayLoads[i] 

                newDrawMap = True
                try:
                    GBMap = drawMap(1) # 1 = GB
                    hi/0 # sometimes drawing the map using the geopy throws an error due to internet connection so just skipping on purpose
                    for c in range(len(energyCustomers)):
                        demandSize = energyCustomers[c].totalNLDemand/maxResDayDemand
                #        demandSize = energyCustomers[c].totalNLDemand/maxDayDemand
                        loc = energyCustomers[c].location
                        custName = energyCustomers[c].name
                        GBMap.setCity(loc,demandSize,custName)
                    print('Geopy successful.')
                except:
                    GBMap = oldDrawMap(1)
                    newDrawMap = False
                    for c in range(len(energyCustomers)):
                        demandSize = energyCustomers[c].totalNLDemand/maxResDayDemand
               #         demandSize = energyCustomers[c].totalNLDemand/maxDayDemand
                        loc = energyCustomers[c].location
                        custName = energyCustomers[c].name
                        GBMap.setCity(loc,demandSize,custName)
                    print('Geopy unsuccessful. Using old version.')
                GBMap.drawCities()

            #--------------------------------------------------------------------
            

        

        
        ##########################################################################
        ################ End of year, update model for next year #################
        ##########################################################################

        # record curtailment
        hourlyCurtailPerYear.append(hourlyCurtail)#hourlyCurtail8760 ; hourlyCurtailPerYear many years
        tempCurtailCount = 0
        for k in range(len(hourlyCurtail)):
            if(hourlyCurtail[k]>0):
                tempCurtailCount+=1
        yearlyCurtailedInstances.append(tempCurtailCount)

        # calculating yearly emissions
        sumTotCap = 0.0
        sumDeRateTotCap = 0.0
        yearlyEmissions = 0.0
        for gc in range(len(elecGenCompanies)): # loop through all gen companies
            elecGenCompanies[gc].calculateYearlyProfit() # get profit
            curCap, curDeRateCap = elecGenCompanies[gc].getTotalCapacity() # get installed capacity
            sumTotCap = sumTotCap + curCap # from initial year until now
            sumDeRateTotCap = sumDeRateTotCap + curDeRateCap
            yearlyEmissions = yearlyEmissions + elecGenCompanies[gc].totalEmissionsYear
        
        capacityMargin = sumTotCap - peakDemand # calculate margins
        deRatedCapacityMargin = sumDeRateTotCap - peakDemand

        # calculating capacity capacity per tech per busbar
        nuclearcaplist = [0]*len(nuclearbuslist)
        coalcaplist = [0]*len(coalbuslist)
        windoffcaplist = [0]*len(windoffbuslist) 
        beccscaplist = [0]*len(beccsbuslist)             
        for gc in range(len(elecGenCompanies)):
            for i in range(len(elecGenCompanies[gc].traditionalGen)):
                if(elecGenCompanies[gc].traditionalGen[i].name == 'Nuclear'):        		
                    c = elecGenCompanies[gc].traditionalGen[i].genCapacity
                    b = elecGenCompanies[gc].traditionalGen[i].numbus
                    if(c>0.1 and (not (b in nuclearbuslist))):
                        nuclearbuslist.append(b)
                        nuclearcaplist.append(c)
                    elif(c>0.1 and (b in nuclearbuslist)):
                        indx = nuclearbuslist.index(b)
                        nuclearcaplist[indx] = nuclearcaplist[indx] + c
                    
                elif(elecGenCompanies[gc].traditionalGen[i].name == 'Coal'):        		
                    c = elecGenCompanies[gc].traditionalGen[i].genCapacity
                    b = elecGenCompanies[gc].traditionalGen[i].numbus
                    if(c>0.1 and (not (b in coalbuslist))):
                        coalbuslist.append(b)
                        coalcaplist.append(c)
                    elif(c>0.1 and (b in coalbuslist)):
                        indx = coalbuslist.index(b)
                        coalcaplist[indx] = coalcaplist[indx] + c

                elif(elecGenCompanies[gc].traditionalGen[i].name == 'BECCS'):        		
                    c = elecGenCompanies[gc].traditionalGen[i].genCapacity
                    b = elecGenCompanies[gc].traditionalGen[i].numbus
                    if(c>0.1 and (not (b in beccsbuslist))):
                        beccsbuslist.append(b)
                        beccscaplist.append(c)
                    elif(c>0.1 and (b in beccsbuslist)):
                        indx = beccsbuslist.index(b)
                        beccscaplist[indx] = beccscaplist[indx] + c




            for i in range(len(elecGenCompanies[gc].renewableGen)):
                if(elecGenCompanies[gc].renewableGen[i].name == 'Wind Offshore'):        		
                    c = elecGenCompanies[gc].renewableGen[i].genCapacity
                    b = elecGenCompanies[gc].renewableGen[i].numbus
                    if(c>0.1 and (not (b in windoffbuslist))):
                        windoffbuslist.append(b)
                        windoffcaplist.append(c)
                    elif(c>0.1 and (b in windoffbuslist)):
                        indx = windoffbuslist.index(b)
                        windoffcaplist[indx] = windoffcaplist[indx] + c
        yearlynuclearcaplist.append(nuclearcaplist)                
        yearlycoalcaplist.append(coalcaplist)             
        yearlywindoffcaplist.append(windoffcaplist)
        yearlybeccscaplist.append(beccscaplist)
        
        '''
        # draw pie chart for 30 buses 
        TechBus = list()
        CapBus = list()

        #for bus in range(1,31):
            TechPerBus = list()
           CapPerBus = list()
            for gc in range(len(elecGenCompanies)):
                for i in range(len(elecGenCompanies[gc].traditionalGen)):
                    if(elecGenCompanies[gc].traditionalGen[i].numbus == bus):
                        n = elecGenCompanies[gc].traditionalGen[i].name
                        c = elecGenCompanies[gc].traditionalGen[i].genCapacity
                        if(c>0.1 and (not (n in TechPerBus))):
                            TechPerBus.append(n)
                            CapPerBus.append(c)
                        elif(c>0.1 and (n in TechPerBus)):
                            indx = TechPerBus.index(n)
                            CapPerBus[indx] = CapPerBus[indx] + c
                for i in range(len(elecGenCompanies[gc].renewableGen)):
               #     if(elecGenCompanies[gc].renewableGen[i].numbus == bus):
               #         n = elecGenCompanies[gc].renewableGen[i].name
               #         c = elecGenCompanies[gc].renewableGen[i].genCapacity
                #        if(c>0.1 and (not (n in TechPerBus))):
                 #           TechPerBus.append(n)
                 #           CapPerBus.append(c)
                   #     elif(c>0.1 and (n in TechPerBus)):
                            indx = TechPerBus.index(n)
                            CapPerBus[indx] = CapPerBus[indx] + c
            TechBus.append(TechPerBus)
            CapBus.append(CapPerBus)
                        


        #draw
    
        import seaborn as sns
        import matplotlib
        import matplotlib.pyplot as plt
 
        sns.set_style("whitegrid")
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['font.family']='sans-serif'
 
        matplotlib.rcParams['axes.unicode_minus'] = False

        fig, axs = plt.subplots(5,6, figsize=(50,60), sharey=True) 
        for b in range(0,30):
            data = CapBus[b]
            datapc = list()
            sumdata = sum(data)
            datalabels = TechBus[b]
            for i in range(len(data)):
                valpc = (data[i]/sumdata)*100
                datapc.append(valpc)
                datalabels[i] = datalabels[i] + ': '+str(round(valpc, 2))+'%'
            a = b % 6
            if(b<=5):
                c=0
            elif(b<=11):
                c=1
            elif(b<=17):
                c=2
            elif(b<=23):
                c=3
            else:
                c=4
 
            wedges, texts = axs[c,a].pie(data, wedgeprops=dict(width=0.5), startangle=-40)
            #axs[c,a].pie(data)
            #axs[c,a].legend(datalabels)
            axs[c,a].set_title('Bus '+str(b+1))
            bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
            kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1)/2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                connectionstyle = "angle,angleA=0,angleB={}".format(ang)
                kw["arrowprops"].update({"connectionstyle": connectionstyle})
                axs[c,a].annotate(datalabels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                            horizontalalignment=horizontalalignment, **kw)
        #plt.show()
        
        #plt.save(RESULTS_FILE_PATH+str(BASEYEAR+y)+'.png')

        '''
        ####### Capacity auction ######

        Utils.resetCurYearCapInvest()

        # introduce battery storage in 2018
        # this next part of code should only be used if using a linear increase in battery storage
        
        if(boolEnergyStorage and boolLinearBatteryGrowth and y + BASEYEAR +1 >= 2018):
            prevYearBatteryCap = totalBatteryCap #total discharge rate last year
            total2018BatCap = 3590000
            batCapRange = totalFinalBatteryCap - total2018BatCap
            numY = (BASEYEAR + maxYears -1) - 2018 #(2050-2018) 2010+41-1=2050
            
            if(numY > 1):
                batteryCapYearIncrement = batCapRange/ numY
            else:
                batteryCapYearIncrement = batCapRange

            if(y + BASEYEAR + 1 == 2018):
                totalBatteryCap = total2018BatCap
            else:
                totalBatteryCap = prevYearBatteryCap + batteryCapYearIncrement
            
            batteryCapPerCompany = totalBatteryCap/len(elecGenCompanies)
            for i in range(len(elecGenCompanies)):
                elecGenCompanies[i].removeBatteries()
                elecGenCompanies[i].addBatterySize(batteryCapPerCompany)
                elecGenCompanies[i].curYearBatteryBuild = batteryCapPerCompany
        

        CapPerBus = list()
        for busc in range(1,31):            
            for gc in range(len(elecGenCompanies)):
                for i in range(len(elecGenCompanies[gc].traditionalGen)):
                    if(elecGenCompanies[gc].traditionalGen[i].numbus == busc):
                        c = elecGenCompanies[gc].traditionalGen[i].genCapacity
                        if(len(CapPerBus)==busc-1):
                            CapPerBus.append(c)
                        elif(len(CapPerBus)==busc):
                            CapPerBus[busc-1] = CapPerBus[busc-1] + c
                for i in range(len(elecGenCompanies[gc].renewableGen)):
                    if(elecGenCompanies[gc].renewableGen[i].numbus == busc):
                        c = elecGenCompanies[gc].renewableGen[i].genCapacity
                        if(len(CapPerBus)==busc-1):
                            CapPerBus.append(c)
                        elif(len(CapPerBus)==busc):
                            CapPerBus[busc-1] = CapPerBus[busc-1] + c
            if(len(CapPerBus)==busc-1):
                CapPerBus.append(0)
            elif(len(CapPerBus)>busc):
                input('error')

        PeakDPerBus = list()
        for c in range(0,30):
            tempeakd = max(customerNLs[c])
            PeakDPerBus.append(tempeakd)
        busheadroom = [j-k for j,k in zip(CapPerBus,totalCustDemand)] # 30bus
        yearlyheadroom.append(busheadroom)
        # cfd auction
        policy.cfdAuction(3, 6000000, elecGenCompanies, busheadroom) # 3 years, 6 GW to be commissioned
        # capacity auction
        if(boolLinearBatteryGrowth and boolEnergyStorage):
            policy.capacityAuction(4, peakDemand, elecGenCompanies, False, busheadroom)
        else:
            policy.capacityAuction(4, peakDemand, elecGenCompanies, boolEnergyStorage, busheadroom)

        years.append((BASEYEAR+y))
        yearlyTotCap.append(sumTotCap)
        yearlyDeRCap.append(sumDeRateTotCap)
        yearlyPeakD.append(peakDemand)
        yearlyCapM.append(capacityMargin)
        yearlyDeRCapM.append(deRatedCapacityMargin)
            

        totYearGridGenKWh = totYearTGenKWh + totYearRGenKWh
        gridCO2emisIntens = (yearlyEmissions/totYearGridGenKWh)*1000 # *1000 because want gCO2/kWh not kgCO2
        print('year ',(BASEYEAR+y))
        print('gridCO2emisIntens (gCO2/kWh) ',gridCO2emisIntens)

        
        policy.increaseYear()
        # update CO2 Price for next year
        newCO2Price = policy.getNextYearCO2Price(gridCO2emisIntens)
        policy.recordYearData()

        # update wholesale electricity price
        for gc in range(len(elecGenCompanies)): # loop through all gen companies
            wholesEPriceChange = elecGenCompanies[gc].updateTechnologiesYear(newCO2Price)#wholesEPriceChange returns 0

        # demand elasticity
        for i in range(len(energyCustomers)):
     #       demandChangePC = energyCustomers[i].updateYear(wholesEPriceChange)
            demandChangePC = energyCustomers[i].updateYear(0.0,i) #

        demandCoeff = 1.0 + (demandChangePC/100.0) #how mauch percentage change compared to 2018. e.g. 180%


        # each generation company agent makes decision to invest in new capacity
        for gc in range(len(elecGenCompanies)): # loop through all gen companies
            if(boolLinearBatteryGrowth and boolEnergyStorage):
                elecGenCompanies[gc].updateCapacityDecision(peakDemand, False)
            else:
                elecGenCompanies[gc].updateCapacityDecision(peakDemand, boolEnergyStorage)
                

        batSubsReq = list()
        for gc in range(len(elecGenCompanies)):
            batSubsReq.append(elecGenCompanies[gc].yearlyBatterySubsNeeded)
        
        techT, techCap, techDRCap =  getCapacityPerTech(elecGenCompanies)
        techNamesGraph = techT.copy()

        # draw capacity mix chart
        if((y==0 or y==maxYears-1) and boolDrawGenMixGraph):
            pieName = 'Capacity Mix '+str(BASEYEAR+y)
            Utils.pieChart(techCap,techT,pieName)
            techCapGW = [x / 1000000 for x in techCap]
            Utils.barChart(techCapGW,techT,pieName, 'Capacity (GW)')

        # record information
        if(y==0):
            techTypes = techT
            for i in range(len(techCap)):#10 techs
                tempL = list()
                tempL.append(techCap[i])
                techCapYear.append(tempL) #10 list for 10 tech, each has many years

                tempD = list()
                tempD.append(techDRCap[i])
                techDeRCapYear.append(tempD)
        else:
            for i in range(len(techCap)):
                techCapYear[i].append(techCap[i])
                techDeRCapYear[i].append(techDRCap[i])

       


        for gc in range(len(elecGenCompanies)): # reset values
            elecGenCompanies[gc].resetYearlyValues()

        Utils.resetCurYearCapInvest()









        # writing results to file if at the end of simulation
        if(y== maxYears-1): # End of simulation

            print('battery subs required')
            for k in range(len(batSubsReq)):
                print('k ',k)
                print(batSubsReq[k])
            '''
            try:
                my_np_array = np.array(batSubsReq)
                fileOut = RESULTS_FILE_PATH + 'BatterySubsNeeded.csv'
                pd.DataFrame(my_np_array).to_csv(fileOut, index = False)
            except ZeroDivisionError:
                print('cant convert to numpy and write output')
            '''
                
            if(boolEnergyStorage):
                try:
                    fileOut = RESULTS_FILE_PATH + 'BatterySubsNeeded.csv'
                    newPD =  pd.DataFrame(np.concatenate(batSubsReq))
                    newPD.to_csv(fileOut, index = False)
                except ZeroDivisionError:
                    print('cant convert to numpy and write output v2')
                

      #      input('wait')

            
                

            Utils.graphMultSeriesOnePlotV2(techCapYear, 'Year', 'Capacity (kW)', 'Yearly Capacity',techNamesGraph,years) # techT # techTypes

            capNamesOut = techNamesGraph.copy()
            capNamesOut.insert(0,'Year')
            capDataOut = techCapYear.copy()
            capDataOut.insert(0,years)
            fileOut = RESULTS_FILE_PATH + 'YearlyCapacity.csv'
            Utils.writeListsToCSV(capDataOut,capNamesOut,fileOut)

            fileOut = RESULTS_FILE_PATH + 'YearlyCapFactor.csv'
            capFacNames = genNamesOut.copy()
            capFacData = genDataOut.copy()
            for k in range(len(capFacNames)):
                for l in range(len(capNamesOut)):
                    if(capFacNames[k]==capNamesOut[l] and capFacNames[k]!='Year'):
                        for m in range(len(genDataOut[k])):   #year                         
                            actGen = genDataOut[k][m]
                            tempCap = capDataOut[l][m]
                            if(actGen<0.001 or tempCap<0.001):
                                capFacData[k][m] = 0.0
                            else:
                                capFacData[k][m] = 100*actGen/(tempCap*24*365) #hourly average, actgen each hour/capacity 100 convert to percentage
                
            Utils.writeListsToCSV(capFacData,capFacNames,fileOut)


            fileOut = RESULTS_FILE_PATH + 'HourlyCurtailment.csv'
            Utils.writeListsToCSV(hourlyCurtailPerYear,years,fileOut)
            
            fileOut = RESULTS_FILE_PATH + 'HourlyLossOfLoad.csv'
            Utils.writeListsToCSV(hourlyLossOfLoadPerYear,years,fileOut)
            


            tempData = list()
            tempNames = list()
            tempData.append(years)
            tempData.append(yearlyTotCap)
            tempData.append(yearlyDeRCap)
            tempData.append(yearlyPeakD)
            tempData.append(yearlyCapM)
            tempData.append(yearlyDeRCapM)
            tempData.append(yearlyCurtailedInstances)
            tempData.append(yearlyLossOfLoadInstances)
            if(boolEnergyStorage):
                tempData.append(annualStorageCap)
            
            tempNames.append('Year')
            tempNames.append('Capacity')
            tempNames.append('Derated Capacity')
            tempNames.append('Peak Demand')
            tempNames.append('Capacity Margin')
            tempNames.append('Derated Capacity Margin')
            tempNames.append('Curtailed Hours')
            tempNames.append('LossOfLoad Hours')
            if(boolEnergyStorage):
                tempNames.append('Annual Storage Capacity')
            fileOut = RESULTS_FILE_PATH + 'YearlySystemEvolution.csv'
            Utils.writeListsToCSV(tempData,tempNames,fileOut)

            policy.writeResultsToFile(RESULTS_FILE_PATH)

            
            for k in range(len(elecGenCompanies)):    
                elecGenCompanies[k].writeToFileAllYears(RESULTS_FILE_PATH,k)

            
            if(boolDrawPolicyGraph):
                policy.yearGraph()
            # if we want to look at individual companies 
            if(boolDrawYearlyCompanies):
                displayCompanies = list()
                displayCompanies.append('E.On UK')
                displayCompanies.append('EDF Energy')
                displayCompanies.append('Scottish power')
                displayCompanies.append('SSE') 
                displayCompanies.append('Centrica')
                
                for i in range(len(elecGenCompanies)):
                    if(elecGenCompanies[i].name in displayCompanies):
                        elecGenCompanies[i].graphAllGensAllYears()


            if(boolDrawYearlyCap):
                graphYearlyCapacity(years, yearlyTotCap, yearlyDeRCap, yearlyPeakD, yearlyCapM, yearlyDeRCapM)

            graphYearlyBus(years, yearlynuclearcaplist, nuclearbuslist, 'Nuclear')
            graphYearlyBus(years, yearlycoalcaplist, coalbuslist, 'Coal') 
            graphYearlyBus(years, yearlywindoffcaplist, windoffbuslist, 'Wind Offshore') 
            graphYearlyBus(years, yearlybeccscaplist, beccsbuslist, 'BECCS')   
            graphheadroom(years, yearlyheadroom)
        ##########################################################################
        ##########################################################################
        ##########################################################################
            


    
   
    











