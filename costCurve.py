import numpy as np


class CostCurve():

    def __init__(self, avgCost, costCurveType):
        self.costCurveType = costCurveType
        self.avgCost = avgCost

 
    # ADD @property getter and setter for the properties
    # 

    def calcCost(self, value):
        # cost curve function to be used to calculate the cost of energy efficiency improvements
        cost = 0
        if self.costCurveType == "linear":
            cost = value * self.avgCost
        return cost