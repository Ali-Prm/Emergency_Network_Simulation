import simpy 
import numpy as np 
import pandas as pd 


from zone import Zone 
from station import Station


# Network class contains essential assumptions and characteristics about the emergency system services:
# The centroid of each zone is used a node for modeling them. 
## 1. It contains number of nodes in the network. Each node can be both supply and demand node. 
## 2. It contains the zone objects which determines a list of neighbors for each node based on travel time ascending order. 
## 3. It contains stations objects, which stores the data for each station and its resources. 
## 4. It contains the OD matrix, travel time between nodes in the network. 
## 5. It contains station and resource configuraion. 
## 6. It contains standard travel time for three different vehicles.
## 7. It contains number of incident and the intial database which contains the location, occurence time, and type of incidents. 
## 8. It stores simulated data after the completion. Output data are stored in different ways, such as final database, utilization database, and zonal database. 


class Network:
    
    def __init__(self,
     od, loc, zone_num,
     time_st_t1, time_st_t2, time_st_t3,
     incident_num, initial_db, env):

        # Network characteristics: Nodes in Network, OD Matrix, and Resource Configuarion.
        self.od = od
        self.loc = loc
        self.zone_num = zone_num
        # Simulation Environment.
        self.env = env
        # Standard travel time for each type of vehicles.
        self.time_st_t1 = time_st_t1
        self.time_st_t2 = time_st_t2
        self.time_st_t3 = time_st_t3
        
        # Dictonary containing zone objects.
        self.zones = {}
        # List of zone id (node) with station and each type of vehicles.
        self.station_zone_num = []
        self.station_zone_num_t1 = []
        self.station_zone_num_t2 = []
        self.station_zone_num_t3 = []
        
        # Dictionary containing station objects
        self.stations = {}
        
        # Initial incident database 
        self.initial_db = initial_db
        # Incident database (Simulated data are store in a dictionary because of its memory advantages.)
        self.db = {i:{} for i in range(1,incident_num+1)}
        # Final incident database
        self.final_db = None
        self.final_db_cleaned = None 
        # Station's utilization database
        self.station_util_dict = {}  
        self.station_util_db = None 
        # Aggregated zonal incident database
        self.zonal_dict = {i:{} for i in range(1,self.zone_num+1)}
        self.zonal_db = None
        self.zonal_db_e1 = None
        self.zonal_db_e2 = None
        self.zonal_db_e3 = None
        
    
    def generate_zone(self):
        """
        Generating objects from the zone class for each node in the network.
        """
        # Iterating through number of nodes and creating zone object for each.  
        for i in range(1,self.zone_num+1):
            self.zones[str(i)] = Zone(tt=self.od[str(i)], num_id=str(i),
                                      time_st_t1=self.time_st_t1, time_st_t2=self.time_st_t2, time_st_t3=self.time_st_t3,
                                      net=self)
            # After creating each zone object determine a list of neighbors for each based on travel time ascending order.
            self.zones[str(i)].get_nearest()

    def generate_zone_nearest(self):
        """
        Double checking a list of neighbors for each based on travel time ascending order.
        """
        for i in range(1,self.zone_num+1):
            self.zones[str(i)].gt_nearest()
    

    
    def generate_station(self):
        """
        Generating station objects based on resource configuration. 
        """
        # Extracting the list of zone id with station and each type of vehicle. 
        self.station_zone_num = self.loc['Station'][self.loc['Station']==1].index.tolist()
        self.station_zone_num_t1 = self.loc['t1'][self.loc['t1']>=1].index.tolist()
        self.station_zone_num_t2 = self.loc['t2'][self.loc['t2']>=1].index.tolist()
        self.station_zone_num_t3 = self.loc['t3'][self.loc['t3']>=1].index.tolist()
        
        # Generating station objects. First, create a empty station, and then assign their vehicles to them. 
        for i in  self.station_zone_num:
            self.stations[i] = Station(i, {'t1':0, 't2':0,'t3':0}, {'t1':0, 't2':0, 't3':0},
                                       {'t1':0, 't2':0, 't3':0},{'t1':0, 't2':0, 't3':0})
            if i in self.station_zone_num_t1:
                self.stations[i].vehicles['t1'] = self.loc.loc[i,'t1']
                self.stations[i].availability['t1'] = self.loc.loc[i,'t1']
            if i in self.station_zone_num_t2:
                self.stations[i].vehicles['t2'] = self.loc.loc[i,'t2']
                self.stations[i].availability['t2'] = self.loc.loc[i,'t2']
            if i in self.station_zone_num_t3:
                self.stations[i].vehicles['t3'] = self.loc.loc[i,'t3']
                self.stations[i].availability['t3'] = self.loc.loc[i,'t3']
    
    
    def generate_result(self):
        """
        Create the final database from simulated data stored in the dictionary format.
        The final database stores information about each incident. 
        """
        # Creating a copy from initial database to be filled with the simulated data. 
        data = self.initial_db.copy()
        # Converting simulated data from dictionary format to a pandas dataframe. 
        df_res = pd.DataFrame.from_dict(self.db,orient='index')
        self.final_db = pd.merge(data, df_res, left_index=True, right_index=True, how='inner')
        # Creating copy from final database to extract the desired outputs.
        self.final_db_cleaned = self.final_db.copy()
        self.final_db_cleaned[['btt_t1_1']] = self.final_db_cleaned[['ftt_t1_1']]
        self.final_db_cleaned[['btt_t2_1']] = self.final_db_cleaned[['ftt_t2_1']]
        self.final_db_cleaned[['btt_t2_2']] = self.final_db_cleaned[['ftt_t2_2']]
        self.final_db_cleaned[['btt_t3_1']] = self.final_db_cleaned[['ftt_t3_1']]
        self.final_db_cleaned['dt_start_op'] = self.final_db_cleaned['all_arriving_time']-self.final_db_cleaned['inc_time']
        # Arranging columns in the processed database. 
        self.final_db_cleaned = self.final_db_cleaned[['inc_time','inc_type', 'location', 'dact',
                  'within_st_t1','traversed_station_t1_1', 'st_t1_1','ftt_t1_1','btt_t1_1',
                  'within_st_t2','traversed_station_t2_1', 'st_t2_1','ftt_t2_1','btt_t2_1',
                  'traversed_station_t2_2', 'st_t2_2','ftt_t2_2','btt_t2_2',                              
                  'within_st_t3', 'traversed_station_t3_1', 'st_t3_1','ftt_t3_1','btt_t3_1',
                  'dt_start_op',
                  'all_arriving_time',
                  'all_returning_time']]
        self.final_db_cleaned.fillna(0, inplace=True)


    # computed utilization and operation time for each type of vehicle in each station
    def compute_util(self):
        """
        Computing the vehicles' utilization parameters.
        First, extract the whole operation time for each vehicle from output database.
        Then store the operation time and utilization parameter of each vehicle in staion objects. 
        """
        # Getting a view from output database to extract operation time data. 
        df = self.final_db_cleaned
        # Iterate through stataions and update the operation time and utilization parameter for their vehicles.
        for i in  self.station_zone_num :
            # type1 vehicle utilization
            if self.stations[i].vehicles['t1'] == 0:
                self.stations[i].operation_time['t1'] = 'Not Defined'
                self.stations[i].utilization['t1'] = 'Not Defined'
            else :
                if len(df[df['st_t1_1']==i]) > 0 :
                    self.stations[i].operation_time['t1'] = df[df['st_t1_1']==i][['dt_start_op','dact','btt_t1_1']].sum(axis=1).sum()
                    self.stations[i].utilization['t1'] = self.stations[i].operation_time['t1']/(self.stations[i].vehicles['t1']*self.env._now)
                else :
                    self.stations[i].operation_time['t1'] = 0
                    self.stations[i].utilization['t1'] = 0
                
            # type3 vehicle utilization
            if self.stations[i].vehicles['t3'] == 0:
                self.stations[i].operation_time['t3'] = 'Not Defined'
                self.stations[i].utilization['t3'] = 'Not Defined'
            else:
                if len(df[df['st_t3_1']==i]) > 0 :
                    self.stations[i].operation_time['t3'] = df[df['st_t3_1']==i][['dt_start_op','dact','btt_t3_1']].sum(axis=1).sum()
                    self.stations[i].utilization['t3'] = self.stations[i].operation_time['t3']/(self.stations[i].vehicles['t3']*self.env._now)
                else :
                    self.stations[i].operation_time['t3'] = 0
                    self.stations[i].utilization['t3'] = 0
                
            # type2 vehicle utilization 
            if self.stations[i].vehicles['t2'] == 0:
                self.stations[i].operation_time['t2'] = 'Not Defined'
                self.stations[i].utilization['t2'] = 'Not Defined'
            else:
                if len(df[df['st_t2_1']==i]) | len(df[df['st_t2_1']==i]) > 0:
                    t2_1 = df[df['st_t2_1']==i][['dt_start_op','dact','btt_t2_1']].sum(axis=1).sum()
                    t2_2 = df[df['st_t2_2']==i][['dt_start_op','dact','btt_t2_2']].sum(axis=1).sum()
                    self.stations[i].operation_time['t2'] = t2_1+t2_2
                    self.stations[i].utilization['t2'] = (t2_1+t2_2)/(self.stations[i].vehicles['t2']*self.env._now)
                else :
                    self.stations[i].operation_time['t2'] = 0
                    self.stations[i].utilization['t2'] = 0
    
    
    def generate_station_db(self):
        """
        Generating the vehicles' utilization database.  
        """
        for i in  self.station_zone_num:
            self.station_util_dict[i] = {}
            self.station_util_dict[i]['t1_util'] = self.stations[i].utilization['t1']
            self.station_util_dict[i]['t2_util'] = self.stations[i].utilization['t2']
            self.station_util_dict[i]['t3_util'] = self.stations[i].utilization['t3']

        self.station_util_db = pd.DataFrame.from_dict(self.station_util_dict,orient='index')
     
    
    
    def generate_zonal_db(self):
        """
        Generating database containg aggregated data about each type of incident on the zonal level.
        First, processed inforamtion are stored in dictionary format because of its memory advantages.
        Then, it is converted to a pandas dataframe. 
        """
        # Getting a copy from final output.
        df = self.final_db_cleaned.copy()
        # Standard travel time
        standard = {'t1':self.time_st_t1, 't2':self.time_st_t2, 't3':self.time_st_t3}

        # Triple-level for loop: incidents' type --> zones --> vehicles 
        ## (level-1) `j` for incident's type.
        for j in [1,2,3]:
            if j == 3 : #Type-3 incident.
                vehicle_type = ['t1_1','t2_1','t2_2','t3_1']
            elif j ==2 : #Type-2 incident
                vehicle_type = ['t1_1','t2_1','t2_2']
            elif j==1 : #Type-1 incident
                vehicle_type = ['t1_1','t2_1']
            ## (level-2) `i` for zones.
            for i in range(1,self.zone_num+1):
                # i for each zone
                d = df[(df['location']==i)&(df['inc_type']==j)]
                self.zonal_dict[i][f'num_e{j}'] = len(d)
                ## (level-3) `t` for vehicles' type.
                for t in vehicle_type:
                    t_m = t.split('_')[0]
                    # Number of incidents within or not within standard
                    self.zonal_dict[i][f'e{j}_{t}_wst'] = len(d[d[f'ftt_{t}']<=standard[t_m]])
                    self.zonal_dict[i][f'e{j}_{t}_nst'] = len(d)-len(d[d[f'ftt_{t}']<=standard[t_m]])
                    # Average travel time 
                    self.zonal_dict[i][f'e{j}_{t}_mt_wst'] = d[d[f'ftt_{t}']<=standard[t_m]][f'ftt_{t}'].mean()
                    self.zonal_dict[i][f'e{j}_{t}_mt_nst'] = d[d[f'ftt_{t}']>standard[t_m]][f'ftt_{t}'].mean()
                    self.zonal_dict[i][f'e{j}_{t}_mt'] = d[f'ftt_{t}'].mean()
                    # Traversering data
                    trvs_dict = d[f'traversed_station_{t}'].value_counts().to_dict()
                    for num_trvs,nums in trvs_dict.items():
                        self.zonal_dict[i][f'e{j}_{t}_trvs_{num_trvs}'] = nums
        
        # Coverage of each incident type 
        for i in range(1,self.zone_num+1):  
            e1_df = df[(df['location']==i)&(df['inc_type']==1)]
            e2_df = df[(df['location']==i)&(df['inc_type']==2)]
            e3_df = df[(df['location']==i)&(df['inc_type']==3)]
            self.zonal_dict[i]['num_cov_e1'] = len(e1_df[(e1_df['ftt_t1_1']<=standard['t1'])&(e1_df['ftt_t2_1']<=standard['t2'])])
            self.zonal_dict[i]['num_cov_e2'] = len(e2_df[(e2_df['ftt_t1_1']<=standard['t1'])&(e2_df['ftt_t2_1']<=standard['t2'])&(e2_df['ftt_t2_2']<=standard['t2'])])
            self.zonal_dict[i]['num_cov_e3'] = len(e3_df[(e3_df['ftt_t1_1']<=standard['t1'])&(e3_df['ftt_t2_1']<=standard['t2'])&(e3_df['ftt_t2_2']<=standard['t2'])&(e3_df['ftt_t3_1']<=standard['t3'])])
            
        # Extracting related columns for each type of incident.
        col_e1 = []
        col_e2 = []
        col_e3 = []
        # Changing data formats.
        self.zonal_db = pd.DataFrame.from_dict(self.zonal_dict,orient='index')
        # Spiliting columns containing data about different type of incidents. 
        for key in self.zonal_db.columns:
            if 'e1' in key:
                col_e1.append(key)
            elif 'e2' in key:
                col_e2.append(key)
            elif 'e3' in key:
                col_e3.append(key)
        self.zonal_db_e1 = self.zonal_db[col_e1]
        self.zonal_db_e2 = self.zonal_db[col_e2]
        self.zonal_db_e3 = self.zonal_db[col_e3]
        
        ### 1. Coverage 
        # Computing coverage of each incidents.
        # Type-1 (e1) incident
        df_e1 = self.zonal_db_e1.copy()
        df_e1['cov_t1_1'] = df_e1.apply(lambda x: x.e1_t1_1_wst/x.num_e1 if x.num_e1>0 else 0, axis=1)
        df_e1['cov_t2_1'] = df_e1.apply(lambda x: x.e1_t2_1_wst/x.num_e1 if x.num_e1>0 else 0, axis=1)
        df_e1['cov_e1'] = df_e1.apply(lambda x: x.num_cov_e1/x.num_e1 if x.num_e1>0 else 0, axis=1)
        self.zonal_db_e1 =  df_e1
        # Type-2 (e2) incident
        df_e2 = self.zonal_db_e2.copy()
        df_e2['cov_t1_1'] = df_e2.apply(lambda x: x.e2_t1_1_wst/x.num_e2 if x.num_e2>0 else 0, axis=1)
        df_e2['cov_t2_1'] = df_e2.apply(lambda x: x.e2_t2_1_wst/x.num_e2 if x.num_e2>0 else 0, axis=1)
        df_e2['cov_t2_2'] = df_e2.apply(lambda x: x.e2_t2_2_wst/x.num_e2 if x.num_e2>0 else 0, axis=1)
        df_e2['cov_e2'] = df_e2.apply(lambda x: x.num_cov_e2/x.num_e2 if x.num_e2>0 else 0, axis=1)
        self.zonal_db_e2 =  df_e2
        # Type-3 (e3) incident
        df_e3 = self.zonal_db_e3.copy()
        df_e3['cov_t1_1'] = df_e3.apply(lambda x: x.e3_t1_1_wst/x.num_e3 if x.num_e3>0 else 0, axis=1)
        df_e3['cov_t2_1'] = df_e3.apply(lambda x: x.e3_t2_1_wst/x.num_e3 if x.num_e3>0 else 0, axis=1)
        df_e3['cov_t2_2'] = df_e3.apply(lambda x: x.e3_t2_2_wst/x.num_e3 if x.num_e3>0 else 0, axis=1)
        df_e3['cov_t3_1'] = df_e3.apply(lambda x: x.e3_t3_1_wst/x.num_e3 if x.num_e3>0 else 0, axis=1)
        df_e3['cov_e3'] = df_e3.apply(lambda x: x.num_cov_e3/x.num_e3 if x.num_e3>0 else 0, axis=1)
        self.zonal_db_e3 =  df_e3

        # Filling NA values with zero
        self.zonal_db_e1.fillna(0,inplace=True)
        self.zonal_db_e2.fillna(0,inplace=True)
        self.zonal_db_e3.fillna(0,inplace=True)
        
        ### 2. Traversing data 
        # Computing average number of traverse 
        df_e1 = self.zonal_db_e1.copy()
        df_e2 = self.zonal_db_e2.copy()
        df_e3 = self.zonal_db_e3.copy()
        # Type-1 (e1) incident
        e1_t1_col = []
        e1_t2_col = []
        for col in  df_e1.columns:
            if ('t1' in col) & ('trvs' in col):
                e1_t1_col.append(col)
            if ('t2_1' in col) & ('trvs' in col):
                e1_t2_col.append(col)
        for ind,row in df_e1.iterrows():
            x_t1 = 0
            x_t2 = 0
            for col in e1_t1_col:
                num = float(col.split('_')[-1])
                x_t1 += num*row[col]
            for col in e1_t2_col:
                num = float(col.split('_')[-1])
                x_t2 += num*row[col]
            if df_e1.loc[ind,'num_e1'] >0 :
                x_t1 = x_t1/df_e1.loc[ind,'num_e1']
                x_t2 = x_t2/df_e1.loc[ind,'num_e1']
            else :
                x_t1 = 0
                x_t2 = 0
            df_e1.loc[ind,'e1_t1_trvs'] = x_t1
            df_e1.loc[ind,'e1_t2_trvs'] = x_t2
            df_e1.loc[ind,'e1_trvs'] = np.average([x_t1,x_t2])
        self.zonal_db_e1 =  df_e1
    
        # Type-2 (e2) incident
        e2_t1_col = []
        e2_t2_1_col = []
        e2_t2_2_col = []
        for col in  df_e2.columns:
            if ('t1' in col) & ('trvs' in col):
                e2_t1_col.append(col)
            if ('t2_1' in col) & ('trvs' in col):
                e2_t2_1_col.append(col)
            if ('t2_2' in col) & ('trvs' in col):
                e2_t2_2_col.append(col)
        for ind,row in df_e2.iterrows():
            x_t1 = 0
            x_t2_1 = 0
            x_t2_2 = 0
            for col in e2_t1_col:
                num = float(col.split('_')[-1])
                x_t1 += num*row[col]
            for col in e2_t2_1_col:
                num = float(col.split('_')[-1])
                x_t2_1 += num*row[col]
            for col in e2_t2_2_col:
                num = float(col.split('_')[-1])
                x_t2_2 += num*row[col]
            if df_e2.loc[ind,'num_e2'] >0 :
                x_t1 = x_t1/df_e2.loc[ind,'num_e2']
                x_t2_1 = x_t2_1/df_e2.loc[ind,'num_e2']
                x_t2_2 = x_t2_2/df_e2.loc[ind,'num_e2']
            else :
                x_t1 = 0
                x_t2_1 = 0
                x_t2_2 = 0
            df_e2.loc[ind,'e2_t2_1_trvs'] = x_t2_1
            df_e2.loc[ind,'e2_t2_2_trvs'] = x_t2_2
            df_e2.loc[ind,'e2_t1_trvs'] = x_t1
            df_e2.loc[ind,'e2_t2_trvs'] = np.average([x_t2_1,x_t2_2])
            t2_avg = np.average([x_t2_1,x_t2_2])
            df_e2.loc[ind,'e2_trvs'] = np.average([x_t1,t2_avg])
        self.zonal_db_e2 =  df_e2
        
        # Type-3 (e3) incident
        e3_t1_col = []
        e3_t2_1_col = []
        e3_t2_2_col = []
        e3_t3_col = []
        for col in  df_e3.columns:
            if ('t1' in col) & ('trvs' in col):
                e3_t1_col.append(col)
            if ('t2_1' in col) & ('trvs' in col):
                e3_t2_1_col.append(col)
            if ('t2_2' in col) & ('trvs' in col):
                e3_t2_2_col.append(col)
            if ('t3' in col) & ('trvs' in col):
                e3_t3_col.append(col)
        for ind,row in df_e3.iterrows():
            x_t1 = 0
            x_t2_1 = 0
            x_t2_2 = 0
            x_t3 = 0
            for col in e3_t1_col:
                num = float(col.split('_')[-1])
                x_t1 += num*row[col]
            for col in e3_t2_1_col:
                num = float(col.split('_')[-1])
                x_t2_1 += num*row[col]
            for col in e3_t2_2_col:
                num = float(col.split('_')[-1])
                x_t2_2 += num*row[col]
            for col in e3_t3_col:
                num = float(col.split('_')[-1])
                x_t3 += num*row[col]
            if df_e3.loc[ind,'num_e3'] >0 :
                x_t1 = x_t1/df_e3.loc[ind,'num_e3']
                x_t2_1 = x_t2_1/df_e3.loc[ind,'num_e3']
                x_t2_3 = x_t2_2/df_e3.loc[ind,'num_e3']
                x_t3 = x_t3/df_e3.loc[ind,'num_e3']
            else :
                x_t1 = 0
                x_t2_1 = 0
                x_t2_2 = 0
                x_t3 = 0
            df_e3.loc[ind,'e3_t2_1_trvs'] = x_t2_1
            df_e3.loc[ind,'e3_t2_2_trvs'] = x_t2_2
            df_e3.loc[ind,'e3_t1_trvs'] = x_t1
            df_e3.loc[ind,'e3_t2_trvs'] = np.average([x_t2_1,x_t2_2])
            df_e3.loc[ind,'e3_t3_trvs'] = x_t3
            t2_avg = np.average([x_t2_1,x_t2_2])
            df_e3.loc[ind,'e3_trvs'] = np.average([x_t1,t2_avg,x_t3])
        self.zonal_db_e3 =  df_e3