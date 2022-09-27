import simpy
import numpy as np 
import pandas as pd 


# Call arrival modeles the steps each incident goes through. 
# It is the heart of this simulation model and implements the logic of the model. 
# It receives a simulation environment, a network object, incident id, incident's occurence time, incident type, incident's location, and action (service) time.
## The discrete events of the simulation model are:
### 1. Incident Arrival Event: Events are generated when `incident_process` function is called. 
### 2. Vehicles' Arrival Event: After the incidetn's occurenece, the nearest available vehicles are assigned to the incident.
### 3. Service Event: After the required vehicles are arrived, the service event gets started. 
### 4. Vehicles' Return Event: After the service time is passed, vehicles return to their stations. 


def call_arrival(env, count, time, incident_type_id, location, network, incident_type, dact):
    """
    Modeling the steps each incidents goes through. 
    """

    ### `EVENYT-1` : Incident Arrival Event

    # Simulation Clock at incident arrival event.
    starting = env.now

    # Dictionary containing the required vehicles based on incident type. 
    required_vehicles = incident_type[incident_type_id]
    
    # Iterate over the required vehicles dictionary and find the nearest available vehicles. 
    ## key : vehicle type
    ## value : number of required vehicles of each type 
    for key,value in required_vehicles.items():
        # Only search for the required vehicles. 
        if value > 0 :
            # Iterate to find the required number of vehicles.
            for i in range(value):
                # First, search within standard travel time.
                if bool(network.zones[str(location)].nearest[f'nearest_st_{key}']) & \
                    any([ network.stations[ind].availability[key] for ind in network.zones[str(location)].nearest[f'nearest_st_{key}']]):
                    # Count the number of traversed stations in the nearest list before finding first available vehicle. 
                    num = 0
                    # Iterate through list of stations within standard travel time and find the stations with the required vehicles. 
                    for j in network.zones[str(location)].nearest[f'nearest_st_{key}']:
                        num += 1
                        # Check if there are available vehicles.
                        if network.stations[j].availability[key] >0 :
                            # Store the travel time of the nearest available vehicle. 
                            network.db[count][f'st_{key}_{i+1}'] = j
                            if key == 't1':
                                network.db[count][f'ftt_{key}_{i+1}'] = 0.9 * network.zones[str(location)].tt[j]            
                            elif key == 't3':
                                network.db[count][f'ftt_{key}_{i+1}'] = 1.01 * network.zones[str(location)].tt[j]
                            else :   
                                network.db[count][f'ftt_{key}_{i+1}'] = network.zones[str(location)].tt[j]
                        
                            # Change the availability of vehicles in the chosen station.
                            network.stations[j].availability[key] = max(network.stations[j].availability[key]-1, 0)
                            # Store that this incident is responded within standard travel time.
                            network.db[count][f'within_st_{key}']=True
                            break
                
                # If there are no station within standard time search for staions beyond standard travel time. 
                else:
                    # Count the number of traversed stations in the nearest list before finding first available vehicle. 
                    num = 0
                    # Iterate through list of stations beyond standard travel time and find the stations with the required vehicles.
                    for j in network.zones[str(location)].nearest[f'nearest_nst_{key}']:
                        num +=1
                        # Check if there are available vehicles.
                        if network.stations[j].availability[key] > 0 :
                            # Store the travel time of the nearest available vehicle. 
                            network.db[count][f'st_{key}_{i+1}'] = j
                            if key == 't1':
                                network.db[count][f'ftt_{key}_{i+1}'] = 0.9 * network.zones[str(location)].tt[j]            
                            elif key == 't3':
                                network.db[count][f'ftt_{key}_{i+1}'] = 1.01 * network.zones[str(location)].tt[j]
                            else :   
                                network.db[count][f'ftt_{key}_{i+1}'] = network.zones[str(location)].tt[j]
                                
                            # Change the availability of vehicles.
                            network.stations[j].availability[key] = max(network.stations[j].availability[key]-1, 0)
                            # Store that this incident is not responded within standard travel time.
                            network.db[count][f'within_st_{key}']=False
                            break
                # Store the number of traversed stations before finding first available vehicles. 
                network.db[count][f'traversed_station_{key}_{i+1}'] = num 
                
    
    # Storing the travel time of each vehicles.
    ## Storing this data allows us to return each vehicle to their stations based on their specific travel time. 
    network.db[count]['arrivals'] = []
    for key,value in required_vehicles.items():
        for i in range(value):
            network.db[count]['arrivals'].append(network.db[count][f'ftt_{key}_{i+1}'])
    # Sorting the travel time allows us to schedule the vehicles' return in a corret order. 
    network.db[count]['arrivals'].sort()
    # Create dictonary of {travel time : st_key_value}  
    network.db[count]['arrival_dict'] = {}
    for arr in network.db[count]['arrivals']:
        for key,value in required_vehicles.items():
            for i in range(value):
                if network.db[count][f'ftt_{key}_{i+1}'] == arr:
                    network.db[count]['arrival_dict'][arr] = (network.db[count][f'st_{key}_{i+1}'],key)
    # Compute time difference between traveling time of required vehicles for invcident.
    ## The list is created from sorted travel time list.
    network.db[count]['int_arr'] = [network.db[count]['arrivals'][i+1]-network.db[count]['arrivals'][i] for i in range(len(network.db[count]['arrivals'])-1)]
    
    # Find the maximum travel time of the required vehicles for scheduling the service event. 
    network.db[count]['max_arrivals'] = np.max(network.db[count]['arrivals'])
    
    ### `EVENT-2`: Vehicles' Arrival Event.
    yield env.timeout(network.db[count]['max_arrivals'])
    network.db[count]['all_arriving_time'] = env.now 

    ### `Event-3`: Servie Event.
    yield env.timeout(dact)


    ### `Event-4`: Vehicles' Return Event 
    # Send back first vehicle to thier station based on their travel time. 
    first_vehicle_arriving = network.db[count]['arrivals'][0]
    first_arriving_station, type_vehic = network.db[count]['arrival_dict'][first_vehicle_arriving]
    # First vehicle arrivng at its station
    yield env.timeout(first_vehicle_arriving)
    # Change the availability of the first vehicle in its station
    network.stations[first_arriving_station].availability[type_vehic] = min(network.stations[first_arriving_station].availability[type_vehic]+1,
                                                                            network.stations[first_arriving_station].vehicles[type_vehic])
    # Send back other vehicles to their stations based on their travel time.
    for intarr,j in zip(network.db[count]['int_arr'],range(len(network.db[count]['int_arr']))):
        tt = network.db[count]['arrivals'][j+1]
        st,t_vehic = network.db[count]['arrival_dict'][tt]
        # Other vehicle arrivng at its station
        yield env.timeout(intarr)
        # Change the availability of the first vehicle in its station
        network.stations[st].availability[t_vehic] = min(network.stations[st].availability[t_vehic]+1,
                                                         network.stations[st].vehicles[t_vehic])
    
    # Store the time all vehicles are returned. 
    network.db[count]['all_returning_time'] = env.now 