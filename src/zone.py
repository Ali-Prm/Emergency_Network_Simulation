import simpy
import numpy as np 
import pandas as pd 


# The zone class gets od matrix, number of nodes, standard travel times, and a object from network class as an input. 
# The zone  
## It creates a list of neigboring supply nodes (staions) based on travel time in an ascending order for each node. 
## For each type of vehicle two lists of neighboring supply node are created: 
### 1. Supply nodes within standard travel time.
### 2. Supply nodes beyond standard travel time. 


class Zone:
    
    def __init__(self,
     tt, num_id,
     time_st_t1, time_st_t2, time_st_t3,
     net):

        # Inputs for the zone class 
        self.tt = tt
        self.num_id = num_id
        self.net = net
        self.time_st_t1 = time_st_t1
        self.time_st_t2 = time_st_t2
        self.time_st_t3 = time_st_t3

        # Finding every two nodes within each vehicle's standard travel time.
        self.zone_st_t1_id = self.tt[self.tt <= self.time_st_t1].sort_values().index.tolist()
        self.zone_st_t2_id = self.tt[self.tt <= self.time_st_t2].sort_values().index.tolist()
        self.zone_st_t3_id = self.tt[self.tt <= self.time_st_t3].sort_values().index.tolist()

        # Finding every two nodes beyond each vehicle's standard travel time.
        self.zone_nst_t1_id = self.tt[self.tt > self.time_st_t1].sort_values().index.tolist()
        self.zone_nst_t2_id = self.tt[self.tt > self.time_st_t2].sort_values().index.tolist()
        self.zone_nst_t3_id = self.tt[self.tt > self.time_st_t3].sort_values().index.tolist()
        
        # Generating dictionary containing relationship between nodes. 
        self.nearest = {'nearest_st_t1':None, 'nearest_st_t2':None,
                        'nearest_nst_t1':None, 'nearest_nst_t2':None,
                        'nearest_st_t3':None, 'nearest_nst_t3':None}
        self.nearest_st_t1 = []
        self.nearest_st_t2 = []
        self.nearest_st_t3 = []
        
        self.nearest_nst_t1 = []
        self.nearest_nst_t2 = []
        self.nearest_nst_t3 = []
    
    
    def get_nearest(self):      
        """
        Finding staions within and beyond each vehicle's standard travel time, based on travel time in an ascending order, for each node.
        """  
        # Type-1 
        ## within standard travel time
        for i in self.zone_st_t1_id :
            if i in self.net.station_zone_num_t1:
                self.nearest_st_t1.append(i)
        ## beyon strandard travel time
        for i in self.zone_nst_t1_id :
            if i in self.net.station_zone_num_t1:
                self.nearest_nst_t1.append(i)     
                
        # Type-2 vehicle
        ## within standard travel time
        for i in self.zone_st_t2_id :
            if i in self.net.station_zone_num_t2:
                self.nearest_st_t2.append(i)
        ## beyon strandard travel time
        for i in self.zone_nst_t2_id :
            if i in self.net.station_zone_num_t2:
                self.nearest_nst_t2.append(i)   
                
        # Type-3 vehicle
        ## within standard travel time
        for i in self.zone_st_t3_id :
            if i in self.net.station_zone_num_t3:
                self.nearest_st_t3.append(i)  
        ## beyon strandard travel time
        for i in self.zone_nst_t3_id :
            if i in self.net.station_zone_num_t3:
                self.nearest_nst_t3.append(i)          
                
                
                
    def gt_nearest(self):
        """
        Storing the result in an attribute called nearest. 
        """
        self.nearest['nearest_st_t1'] = self.nearest_st_t1
        self.nearest['nearest_st_t2'] = self.nearest_st_t2
        self.nearest['nearest_st_t3'] = self.nearest_st_t3
        
        self.nearest['nearest_nst_t1'] = self.nearest_nst_t1
        self.nearest['nearest_nst_t2'] = self.nearest_nst_t2
        self.nearest['nearest_nst_t3'] = self.nearest_nst_t3
                