import simpy
import numpy as np 
import pandas as pd 
from collections import namedtuple
import time
import matplotlib.pyplot as plt

from zone import Zone 
from station import Station
from network import Network

from call_arrival import call_arrival
from incident_process import incident_process


# Loading input data for simulation model
## 1. Resource configuration
loc = pd.read_csv('data/Resource_Configurations/config_2.csv',dtype={'zone': np.str_})
## 2. Incident realization
incident = pd.read_csv('data/Arrivals/arrival_2.csv', index_col='num')
# ## 3. OD matrix 
od = pd.read_csv('data/OD_Matrix/od_2.csv',dtype={'zone': np.str_})


# Assumptions 
## 1. Incidetns types and their required vehicles 
incident_type = {1:{'t1':1, 't2':1},
                 2:{'t1':1, 't2':2},
                 3:{'t1':1, 't2':2, 't3':1}}

# 2. Standard travel time for different vehicles (seconds)
time_st_t1 = 9*60
time_st_t2 = 9*60
time_st_t3 = 14*60

# Number of zones (node) in the network 
zone_num = 693

start = time.time()

# Setup the simulation environment 
env = simpy.Environment()
# Create network object 
network = Network( od, loc, zone_num, time_st_t1, time_st_t2, time_st_t3, len(incident), incident,env)
# Call network object's method to create zones and stations 
network.generate_zone()
network.generate_zone_nearest()
network.generate_station()
network.generate_zone()
network.generate_zone_nearest()
# Generate the events process for each incidents 
env.process(incident_process(env, incident, network,incident_type))
# Run the simulation model
env.run()

# Generate the output database 
network.generate_result()
# Compute and generate utilization data
network.compute_util()
network.generate_station_db()
# Generate output databased for each zones 
network.generate_zonal_db()


end = time.time()

print(end-start)