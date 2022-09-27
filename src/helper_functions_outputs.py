import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import geopandas as gpd 


def process_data(result, fields, param):
    """
    Generating datasets containing performance parameters in a common format for different replications.
    """
    # Generate emepty output
    data = {config:{field:None for field in fields} for config in result.keys()}
    # Iterate through different configurations
    for key in result.keys():
        # Generate dictionary to extrac inforamtion from different runs. 
        dicted_data = {field:[] for field in fields}
        
        # Processing utilization data
        if param == 'utilization':
            for runs in result[key]:
                runs.station_util_db.replace('Not Defined', 0, inplace=True)
                # run once
                #runs.station_util_db = runs.station_util_db*200
                for field in dicted_data.keys():
                    dicted_data[field].append(runs.station_util_db[field])
                    
        # Processing coverage data
        if param == 'coverage':
            for runs in result[key]:
                dicted_data['cov_e1'].append(runs.zonal_db_e1.cov_e1)
                dicted_data['cov_e2'].append(runs.zonal_db_e2.cov_e2)
                dicted_data['cov_e3'].append(runs.zonal_db_e3.cov_e3)
        
        # Process traversal data
        if param == 'traversal':
            for runs in result[key]:
                dicted_data['e1_trvs'].append(runs.zonal_db_e1.e1_trvs)
                dicted_data['e2_trvs'].append(runs.zonal_db_e2.e2_trvs)
                dicted_data['e3_trvs'].append(runs.zonal_db_e3.e3_trvs)
        
        # Processing travel time data.
        if param =='travel_time_incident':
            for runs in result[key]:
                dicted_data['tt_e1'].append((runs.zonal_db_e1[['e1_t1_1_mt', 'e1_t2_1_mt']].mean(axis=1))/60)
                dicted_data['tt_e2'].append((runs.zonal_db_e2[['e2_t1_1_mt', 'e2_t2_1_mt', 'e2_t2_2_mt']].mean(axis=1))/60)
                dicted_data['tt_e3'].append((runs.zonal_db_e3[['e3_t1_1_mt', 'e3_t2_1_mt', 'e3_t2_2_mt', 'e3_t3_1_mt']].mean(axis=1))/60)
        
        for field in fields:       
            data[key][field] = pd.concat(dicted_data[field], axis=1)

    return data




def box_plots(data, param, configuration_name):
    """
    Creating boxplots of different performance parameter in different replications.
    """
    red_square = dict(markerfacecolor='r', marker='s')
    title_types = ['Type-1', 'Type-2', 'Type-3']
    
    if param == 'utilization':
        fields = ['t1_util', 't2_util', 't3_util']
        title = 'Average Utilization of Vehicle '
        fig, axs = plt.subplots(figsize=(10, 3), ncols=3, nrows=1)
        
    if param == 'coverage':
        fields = ['cov_e1', 'cov_e2', 'cov_e3']
        title = 'Average Coverage of Incident '
        fig, axs = plt.subplots(figsize=(10, 3), ncols=3, nrows=1)
        
    if param == 'traversal':
        fields = ['e1_trvs', 'e2_trvs', 'e3_trvs']
        title = 'Average Number of Traversed Stations for Incident '
        fig, axs = plt.subplots(figsize=(16, 3), ncols=3, nrows=1)
        
        
    if param == 'travel_time_incident':
        fields = ['tt_e1', 'tt_e2', 'tt_e3']
        title = "All Units' Average Travel Time for Incident "
        fig, axs = plt.subplots(figsize=(16, 3), ncols=3, nrows=1)
        
    for ax,field,title_type in zip(axs.flat, fields, title_types):
        
        bp = ax.boxplot(x=[data[i][field].mean().ravel() for i in data.keys()],
                    labels=configuration_name, meanline=True, showmeans=True,
                    meanprops={'color':'red', 'linewidth':2, 'linestyle':'-'},
                    medianprops={'color':'green', 'linewidth':2, 'linestyle':'-'}, 
                    flierprops=red_square, vert=True)
        ax.set_title(f'{title}{title_type}')    
        
    plt.tight_layout()
    plt.show()
    
    
def plot_zonal_results(data, param, configuration_name, zone):
    """
    Plotting performance parameters in zonal resolution.
    """
    
    fig, axs = plt.subplots(figsize=(24, 23), ncols=3, nrows=3) 
    
    # Iterate through different configurations.
    for i, config in zip([0,1,2],configuration_name):

        if param == 'Utilization':
            param_list = ['t1_util','t2_util','t3_util']
            title_list = ['Type-1 Vehicle ', 'Type-2 Vehicle', 'Type-3 Vehicle']
            zone['zone97'] = zone['zone97'].astype(np.str_)
            
        if param == 'Coverage':
            param_list = ['cov_e1', 'cov_e2', 'cov_e3']
            title_list = ['Type-1 Incident', 'Type-2 Incident', 'Type-3 Incident']
            zone['zone97'] = zone['zone97'].astype(np.int64)
            
        if param == 'Traversal':
            param_list = ['e1_trvs', 'e2_trvs', 'e3_trvs']
            title_list = ['Type-1 Incident', 'Type-2 Incident', 'Type-3 Incident']
            zone['zone97'] = zone['zone97'].astype(np.int64)
            
        if param == 'Travel Time':
            param_list = ['tt_e1', 'tt_e2', 'tt_e3']
            title_list = ['Type-1 Incident Average', 'Type-2 Incident Average', 'Type-3 Incident Average']
            zone['zone97'] = zone['zone97'].astype(np.int64)
            
        for j, t, title in zip(param_list, [0,1,2], title_list):
            df = pd.DataFrame({j:data[i][j].mean(axis=1)})
            df = pd.merge(zone,df,left_on='zone97',right_index=True,how='left').fillna(0)
            df.plot(column=j, edgecolor='black', ax=axs[t][i], cmap=plt.cm.Reds, alpha=0.7)
            
            axs[t][i].set_title(f'{config}: {title} {param}')
            axs[t][i].set_xticks([])
            axs[t][i].set_yticks([])
            
    plt.tight_layout()
    plt.show()
    
