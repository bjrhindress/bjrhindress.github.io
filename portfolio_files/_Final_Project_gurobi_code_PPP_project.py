#!/usr/bin/env python
# coding: utf-8

#Import libraries
from gurobipy import *
import numpy as np
import csv
import os
import pandas as pd

#Input Constants (for now)

#Fixed cost of opening a POD
c = 85000

#Quota of acceptable demand met
q = .8

#Cost of a testing kit
k = 43

#penalty for an unserved person
g = 10000

#Scenario probabilities
probs = [.1, .1, .1, .1, .1, .1, .1, .1, .1, .1]


#input distances
#path_d = 'distance_dummy.csv'
#data_d = np.genfromtxt(path_d, dtype = str, delimiter = ',', encoding = 'utf-8-sig')
#d = data_d.astype(np.float)
#d.shape

#read in zipcode_pod_path dataframe
path_zip_pod = 'zipcode_pod_paths.csv'
zip_pod_df = pd.read_csv(path_zip_pod)

#create lookup tables for zip and pod IDs --> info about them 
zip_id_name = zip_pod_df[['Zipcode_ID','Zip_code','Zipcode_PO_Name']].drop_duplicates().sort_values(by=['Zipcode_ID']).values
pod_id_name = zip_pod_df[['POD_ID','POD_Names','POD_Addresses']].drop_duplicates().sort_values(by=['POD_ID']).values

#set up indicies
num_zips = len(zip_id_name)
num_pods = len(pod_id_name)
zips = range(num_zips)
pods = range(num_pods)
scenarios = range(5)

#generate distance and time matrices
miles_zip_pods = np.zeros((num_zips,num_pods))
minutes_zip_pods = np.zeros((num_zips,num_pods))

for index, row in zip_pod_df.iterrows(): 
    
    miles_zip_pods[row['Zipcode_ID'],row['POD_ID']] = row['Total_Miles_Shortest_Path']
    minutes_zip_pods[row['Zipcode_ID'],row['POD_ID']] = row['Total_Minutes_Shortest_Path']

#example usage
zip_id = 5
pod_id = 10    
print("Zip ID " + str(zip_id_name[zip_id,0]) + 
      " is " + str(zip_id_name[zip_id,1]) + 
      " and is named " + str(zip_id_name[zip_id,2]))    

print("POD ID " + str(pod_id_name[pod_id,0]) + 
      " is called " + str(pod_id_name[pod_id,1]) + 
      " and is at the address: " + str(pod_id_name[pod_id,2]))

print("The distance from Zip ID " + str(zip_id) +
      " to POD ID " + str(pod_id) +
      " is  " + str(miles_zip_pods[zip_id,pod_id]) +
      " miles which takes " + str(minutes_zip_pods[zip_id,pod_id]) + " minutes.")

#input distances
path_d = 'new_distance_dummy.csv'
data_d = np.genfromtxt(path_d, dtype = str, delimiter = ',', encoding = 'utf-8-sig')
d = data_d.astype(np.float)
#d.shape
#d = miles_zip_pods
d.shape


#input demand
path_Dem = 'scenario_final_global.csv'
data_Dem = np.genfromtxt(path_Dem, dtype = str, delimiter = ',', encoding = 'utf-8-sig')
Demand = data_Dem.astype(np.float)
Demand.shape


#input capacity
path_Cap = 'capacity_dummy_10k.csv'
data_Cap = np.genfromtxt(path_Cap, dtype = str, delimiter = ',', encoding = 'utf-8-sig')
Capacity = data_Cap.astype(np.float)
Capacity.shape


#set up indicies
pods = range(47)
zips = range(90)
scenarios = range(10)


#set up model object
m = Model("Final_Project")


#set up decision variables

#which POD to set up
x = m.addVars(pods, vtype = GRB.BINARY, name = "x")

#scenario-dependent decisions:

#which pod is assigned to each zip in each scenario
y = m.addVars(zips, pods, scenarios, vtype = GRB.BINARY, name = "y")

#how many people in each zip in each scenario will get treated
t = m.addVars(zips, scenarios, vtype = GRB.INTEGER, lb = 0.0, name = "t")

#how much shortage (r) in each zip in each scenario will not get treated
r = m.addVars(zips, scenarios, vtype = GRB.INTEGER, lb = 0.0, name = "r")


#Objective 1:  Minimize the cost of pod set-up

PODcost = LinExpr()
for j in pods:
    PODcost += x[j]*c


#Objective 2: Minimize the cost to Society

SocietyCost = LinExpr()
for s in scenarios:
    for j in pods:
        for i in zips:
            SocietyCost += probs[s]*(g*r[i,s] + t[i,s]*d[i,j]*y[i,j,s])


#set up weights to capture pareto-optimal frontier

#alpha_values = [0,0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999, 1]
alpha_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0,8]
alpha_values =[0.1]
results = np.zeros([len(alpha_values), 2])


#Constraints

#Constraint 1:  Each zipcode is assigned to one pod in every scenario:

for i in zips:
    for s in scenarios:
        m.addConstr(sum(y[i,j,s] for j in pods) == 1)


#Constraint 2:  The number treated at a pod cannot exceed capacity of the pod 
#AND no one can be treated at a pod if it is not built.

for j in pods:
    for s in scenarios:
        m.addConstr(sum(t[i,s]*y[i,j,s] for i in zips) <= (Capacity[j]*x[j]))


#Constraint 3:  The number treated in a zipcode cannot exceed demand in that zipcode.

for i in zips:
    for s in scenarios:
        m.addConstr(t[i,s] <= Demand[i,s])


#Constraint 4:  Shortage r has to be greater than or equal to the gap between the minimum quota allowed and those treated.

for i in zips:
    for s in scenarios:
        m.addConstr(r[i,s] >= q*Demand[i,s] - t[i,s])


#optimization weighted average iterations

for a in range(len(alpha_values)):
    
    alpha = alpha_values[a]
    
    m.setObjective((alpha*PODcost) + (1-alpha)*SocietyCost, GRB.MINIMIZE)
    
    m.params.MIPGap=0.1
    
    m.optimize()
    
    print("Total POD cost: ", PODcost.getValue())
    print("Total Society cost: ", SocietyCost.getValue())

    results[a,0] = PODcost.getValue()
    results[a,1] = SocietyCost.getValue()
    
    ### Get final values of each variable and expression of interest  
    #create arrays to hold values from Gurobi variables 
    num_scenarios = len(scenarios)
    x_pod = np.zeros((num_pods))
    y_zip_pod = np.zeros((num_zips,num_pods,num_scenarios))
    t_zip_pod = np.zeros((num_zips,num_scenarios))
    r_zip_pod = np.zeros((num_zips,num_scenarios))
    
    #extract x values for pods built
    for p in pods:
        x_pod[p] = m.getVarByName(str('x[' + str(p) + ']')).X
        
    #extract y,t,r values for zipcode-->pod,scenario allocations     
    for z in zips:

        for s in scenarios:
            for p in pods:
                y_zip_pod[z,p,s] = m.getVarByName(str('y[' + str(z) + ',' + str(p) + ',' + str(s) +  ']')).X
        
            t_zip_pod[z,s] = m.getVarByName(str('t[' + str(z) + ',' + str(s) + ']')).X
            r_zip_pod[z,s] = m.getVarByName(str('r[' + str(z) + ',' + str(s) + ']')).X
    
### can now access final results (note, these will change for every alpha iteration): ###
# x_pod[p] 
# y_zip_pod[z,p,s] 
# t_zip_pod[z,s]
# r_zip_pod[z,s]
#zip_id = 5
#pod_id = 10    
#print("Zip ID " + str(zip_id_name[zip_id,0]) + 
#      " is " + str(zip_id_name[zip_id,1]) + 
#      " and is named " + str(zip_id_name[zip_id,2]))    
#
#print("POD ID " + str(pod_id_name[pod_id,0]) + 
#      " is called " + str(pod_id_name[pod_id,1]) + 
#      " and is at the address: " + str(pod_id_name[pod_id,2]))
#
#print("The distance from Zip ID " + str(zip_id) +
#      " to POD ID " + str(pod_id) +
#      " is  " + str(miles_zip_pods[zip_id,pod_id]) +
#      " miles which takes " + str(minutes_zip_pods[zip_id,pod_id]) + " minutes.")


# send pods built to file
x_out = np.ndarray((num_pods,4)).astype(str)
for p in pods: 
    if(x_pod[p]==1):
        x_out[p] = np.append(pod_id_name[p],'build').astype(str)
    else:
        x_out[p] = np.append(pod_id_name[p],'no-build').astype(str)
    
pd.DataFrame(x_out,columns=['ID','Name','Address','To-Build']).to_csv("pods_built_global.csv", index=True)
    #table_df.to_csv(str(table_path.split(".")[0])+'_clean.csv', index=False)



y_out = np.ndarray((num_zips,3+3*num_scenarios)).astype(str)
y_out[:,0:3]=zip_id_name[:,0:3]
headers = ['ID','Zip','Name']
for z in zips:

        for s in scenarios:
            for p in pods:
                if(y_zip_pod[z,p,s]==1):
                    y_out[z,3+3*s] = p
                    
            y_out[z,3+3*s+1] = t_zip_pod[z,s]
            y_out[z,3+3*s+2] = r_zip_pod[z,s]
            if(z==0):
                headers.append('zip_pod_s_%s'%s)
                headers.append('num_assigned_s_%s'%s)
                headers.append('shortage_s_%s'%s)

pd.DataFrame(y_out,columns = headers).to_csv("zip_pods_assignments_global.csv", index=True)

pod_vals = results[:,0]
society_vals = results[:,1]

import matplotlib.pyplot as plt

plt.title("Societal Costs and POD Costs at Alpha")
plt.scatter(pod_vals, society_vals)
plt.xlabel("POD Costs")
plt.ylabel("Society Costs")
plt.show()
