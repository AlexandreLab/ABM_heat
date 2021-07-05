import numpy as np
from csv import reader
import random
import pandas as pd
import os
import os.path

#____________________________________________________________
#
# Class used to do various tasks, e.g. read txt files.
# These methods are all fairly self explanitory
#____________________________________________________________

# Normalize data
def normalize(X):
    # Find the min and max values for each column
    x_min = X.min(axis=0)
    x_max = X.max(axis=0)
    # Normalize
    for x in X:
        for j in range(X.shape[1]):
            x[j] = (x[j]-x_min[j])/(x_max[j]-x_min[j])

def random_pick(some_list, probabilities):
    x = random.uniform(0,1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:break
    return item

def scaleList(myList, PCChange):
    newList = list()
    for i in range(len(myList)):
        x = myList[i]
        newList.append(x + x*(PCChange/100.0))
    return newList

def timeList(myList, PCChange):
    newList = list()
    for i in range(len(myList)):
        x = myList[i]
        newList.append(x*PCChange)
    return newList


def multiplyList(myList, mult):
    newList = list()
    for i in range(len(myList)):
        x = myList[i]
        newList.append(x * mult)
    return newList
    

def loadTextFile(file):
        f = open(file, 'r')
        x = f.readlines()
        f.close()
        for i in range(len(x)):
            x[i]= float(x[i])
        return x

def checkUnits(listOfVals):
    listCopy = listOfVals.copy()
    unit = 'kW'
    if(max(listCopy)<1000):
        unit = 'kW'
    elif(max(listCopy)<1000000):
        unit = 'MW'
        for i in range(len(listCopy)):
            listCopy[i] = listCopy[i]/1000.0
    elif(max(listCopy)<1000000000):
        unit = 'GW'
        for i in range(len(listCopy)):
            listCopy[i] = listCopy[i]/1000000.0
    else:
        unit = 'TW'
        for i in range(len(listCopy)):
            listCopy[i] = listCopy[i]/1000000000.0
    return listCopy, unit


def checkSingleValUnit(val):
    unit = 'kW'
    newVal = 0.0
    if(val<1000):
        unit = 'kW'
        newVal = 0.0
    elif(val<1000000):
        unit = 'MW'
        newVal = val/1000.0
    elif(val<1000000000):
        unit = 'GW'
        newVal = val/1000000.0
    else:
        unit = 'TW'
        newVal = val/1000000000.0
    return newVal, unit


        
    
def checkWeightUnits(listOfVals):
    listCopy = listOfVals.copy()
    unit = 'kg'
    if(max(listCopy)<1000):
        unit = 'kg'
    elif(max(listCopy)<1000000):
        unit = '10E3 kg'
        for i in range(len(listCopy)):
            listCopy[i] = listCopy[i]/1000.0
    elif(max(listCopy)<1000000000):
        unit = '10E6 kg'
        for i in range(len(listCopy)):
            listCopy[i] = listCopy[i]/1000000.0
    else:
        unit = '10E9 kg'
        for i in range(len(listCopy)):
            listCopy[i] = listCopy[i]/1000000000.0
    return listCopy, unit


def graphMultSeriesOnePlot(profiles, xLabel, yLabel, title, legendNames):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    fig.suptitle(title)
    ax1 = fig.add_subplot(111)
    for i in range(len(profiles)):
        newProf, unit = checkUnits(profiles[i])
        ax1.plot(newProf)
    ax1.set_ylabel(unit)
    ax1.set_xlabel(xLabel)
    ax1.legend(legendNames, loc='upper left')
    fig.show()


def graphMultSeriesOnePlotV2(profiles, xLabel, yLabel, title, legendNames, yVals):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    fig.suptitle(title)
    ax1 = fig.add_subplot(111)
    for i in range(len(profiles)):
        newProf, unit = checkUnits(profiles[i])
        ax1.plot(yVals, profiles[i])
    ax1.set_ylabel(yLabel)
    ax1.set_xlabel(xLabel)
    from matplotlib.ticker import MaxNLocator
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.legend(legendNames, loc='upper left')
    fig.show()


def graphMultSeriesOnePlotV3(profiles, xLabel, yLabel, title, legendNames):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    fig.suptitle(title)
    ax1 = fig.add_subplot(111)
    for i in range(len(profiles)):
        newProf, unit = checkUnits(profiles[i])
        ax1.plot(profiles[i])
    ax1.set_ylabel(yLabel)
    ax1.set_xlabel(xLabel)
  #  ax1.legend(legendNames, loc='upper left')
    ax1.legend(legendNames, loc='lower center', ncol=2)
 #   ax1.legend(legendNames, loc='upper center', bbox_to_anchor=(0.5, -0.08),
 #         fancybox=True, shadow=True, ncol=3)
    fig.show()



def graph(profiles, xLabels, yLabels, title, subtitles):
    import matplotlib.pyplot as plt
    
    fig, axs = plt.subplots(len(profiles),1)
    fig.suptitle(title, fontsize=20)
    for i in range(len(profiles)):
        axs[i].plot(profiles[i])
        axs[i].set_ylabel(yLabels[i])
        if(i == len(profiles)-1):
            axs[i].set_xlabel(xLabels[i])
        axs[i].set_title(subtitles[i])
    fig.show()

def singleGraph(profile, xLabel, yLabel, title):
    import matplotlib.pyplot as plt
    
    fig, axs = plt.subplots(2,1)
    fig.suptitle(title, fontsize=20)
    axs[0].plot(profile)
    axs[0].set_ylabel(yLabel)
    axs[0].set_xlabel(xLabel)
    fig.show()


def pieChart(pieData, pieLabels, title):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    
    dataLabels = pieLabels
    data = pieData

    dataPC = list()
    sumDataP = sum(data)
    for i in range(len(data)):
        valPC = (data[i]/sumDataP)*100
        dataPC.append(valPC)
        dataLabels[i] = dataLabels[i] + ': '+str(round(valPC, 2))+' %'

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

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
        ax.annotate(dataLabels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title(title)

  #  plt.show()
    fig.show()


def writeListsToCSV(profiles,profNames,FILEPATH):

#    print('profNames[0] ',profNames[0])
 #   print('profiles[0] ',profiles[0])

    df = pd.DataFrame({profNames[0]: profiles[0]})
    for i in range(1,len(profiles)):
  #      print('profNames[i] ',profNames[i])
  #      print('profiles[i] ',profiles[i])
        dat2 = pd.DataFrame({profNames[i]: profiles[i]})
        df = pd.concat([df, dat2], axis=1)

    df.to_csv(FILEPATH)



    

def writeToCSV(profiles,profNames,FILEPATH):
    df = pd.DataFrame({profNames[0]:profiles[0]})
    for i in range(1,len(profiles)):
        df[profNames[i]] = profiles[i]
    df.to_csv(FILEPATH)


def readCSV(FILEPATH):
    contents = pd.read_csv(FILEPATH)
    return contents


def sumVals(listOfVals):
    sumV=0.0
    for i in range(len(listOfVals)):
        sumV = sumV + listOfVals[i]
    return sumV 


def randomOrderListIndx(myList):
    from random import randint
    randomIndx = list()
    while(len(randomIndx)<len(myList)):
        rI = randint(0,len(myList)-1)
        if(not(rI in randomIndx)):
            randomIndx.append(rI)
    return randomIndx


def barChart(myData, xLabels,name,yLabel):

    import matplotlib.pyplot as plt

    fig = plt.figure()
    fig.suptitle(name, fontsize=20)
    ax1 = fig.add_subplot(111)

    y_pos = np.arange(len(xLabels)) #1,2,3,4,5,...xLabels
    
 #   plt.bar(y_pos, myData, align='center', alpha=0.5)
    plt.bar(y_pos, myData, align='center', color = 'blue')
    plt.xticks(y_pos, xLabels, rotation=20)
    plt.ylabel(yLabel)
    fig.show()



def updateCurYearCapInvest(technologies, curYearCapInvest):
    TECHFILENAME = 'GEN_TYPE_LIST.txt'
    CAPINVESTFILENAME = 'CUR_YEAR_GEN_CAP_INVEST_LIST.txt'
     
    if os.path.isfile(CAPINVESTFILENAME): # already investment in capacity this year      
        file2 = open(CAPINVESTFILENAME, "r") 
        totCurYearCapInvest = file2.read().split('\n')
        file2.close()
        totCurYearCapInvest.pop()

        file2 = open(TECHFILENAME, "r") 
        technologyList = file2.read().split('\n')
        file2.close()
        technologyList.pop()

        for i in range(len(technologies)):
            indx = technologyList.index(technologies[i])
            temp = float(totCurYearCapInvest[indx]) + float(curYearCapInvest[i])
            totCurYearCapInvest[indx] = temp
            

        # delete old file so we can update with new one
        try:
            os.remove(CAPINVESTFILENAME)
        except OSError as e:  ## if failed, report it back to the user ##
            print ("Error: %s - %s." % (e.filename, e.strerror))

        # writing new total capacity to file
        file = open(CAPINVESTFILENAME, "w")
        for i in range(len(totCurYearCapInvest)):
            temp = str(totCurYearCapInvest[i])+'\n'
            file.write(temp)
        file.close()
        
        
    else: # no investment yet
        totCurYearCapInvest = curYearCapInvest
        technologyList = technologies

        file = open(CAPINVESTFILENAME, "w")
        for i in range(len(totCurYearCapInvest)):
            temp = str(totCurYearCapInvest[i])+'\n'
            file.write(temp)
        file.close()



def resetCurYearCapInvest():
    CAPINVESTFILENAME = 'CUR_YEAR_GEN_CAP_INVEST_LIST.txt'

    try:
        os.remove(CAPINVESTFILENAME)
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error: %s - %s." % (e.filename, e.strerror))



def addToCapGenList(genTypeName, curCap, curCapList, technologyList):

    newCapList = curCapList.copy()

    if(len(newCapList)==0):
        for i in range(len(technologyList)):
            if(genTypeName==technologyList[i]):
                newCapList.append(curCap)
            else:
                newCapList.append(0.0)
    else:
        indx = technologyList.index(genTypeName)
        newCapList[indx] += curCap

    return newCapList


def getCurYearCapInvest():
    TECHFILENAME = 'GEN_TYPE_LIST.txt'
    CAPINVESTFILENAME = 'CUR_YEAR_GEN_CAP_INVEST_LIST.txt'
    
    if os.path.isfile(CAPINVESTFILENAME): # already investment in capacity this year      
        file2 = open(CAPINVESTFILENAME, "r") 
        totCurYearCapInvest = file2.read().split('\n')
        file2.close()
        totCurYearCapInvest.pop()

        file2 = open(TECHFILENAME, "r") 
        technologyList = file2.read().split('\n')
        file2.close()
        technologyList.pop()

        return technologyList, totCurYearCapInvest

    else:
        file2 = open(TECHFILENAME, "r") 
        technologyList = file2.read().split('\n')
        file2.close()
        technologyList.pop()

        totCurYearCapInvest = list()

        for i in range(len(technologyList)):
            totCurYearCapInvest.append(0.0)

        return technologyList, totCurYearCapInvest


def getWholesaleEPrice(elecGenCompanies):

    tech = list()
    margeC = list()
    wholesaleEPrice = list()
    nuclearMarginalCost = list()
    for i in range(len(elecGenCompanies)):
        genCo = elecGenCompanies[i]
        for j in range(len(genCo.renewableGen)):
            if(len(genCo.renewableGen[j].marginalCost)>0):
                mCost = genCo.renewableGen[j].marginalCost
                if(len(wholesaleEPrice)==0):
                    wholesaleEPrice = mCost.copy()
                else:
                    for p in range(len(wholesaleEPrice)):
                        if(mCost[p]>wholesaleEPrice[p]):
                            wholesaleEPrice[p] = mCost[p]
            if(not (genCo.renewableGen[j].name in tech) and (genCo.renewableGen[j].genCapacity>10)):
                tech.append(genCo.renewableGen[j].name)
                margeC.append(genCo.renewableGen[j].marginalCost)
                            
        for j in range(len(genCo.traditionalGen)):
            if(genCo.traditionalGen[j].name=='Nuclear' and len(nuclearMarginalCost)==0 and (genCo.traditionalGen[j].genCapacity>10)):
                nuclearMarginalCost = genCo.traditionalGen[j].marginalCost.copy()
            if(len(genCo.traditionalGen[j].marginalCost)>0):
                mCost = genCo.traditionalGen[j].marginalCost
                if(len(wholesaleEPrice)==0):
                    wholesaleEPrice = mCost.copy()
                else:
                    for p in range(len(wholesaleEPrice)):
                        if(mCost[p]>wholesaleEPrice[p]):
                            wholesaleEPrice[p] = mCost[p]
            if(not (genCo.traditionalGen[j].name in tech) and (genCo.traditionalGen[j].genCapacity>10)):
                tech.append(genCo.traditionalGen[j].name)
                margeC.append(genCo.traditionalGen[j].marginalCost)
                

    
    return wholesaleEPrice, nuclearMarginalCost





























































    
