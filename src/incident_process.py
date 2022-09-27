import simpy 
import pandas as pd 
import numpy as np 
from call_arrival import call_arrival 

# Process generator yielding call arrival process.
## It recieve a simulation environment, incident database, network object, and incident type.
### Incident database contains the location, occurence time, action (service) time, and type of incidents.
### According to the occurence time and incident id the call arrival function gets called. 


def incident_process(env, incident, network, incident_type):
    """
    A generator function scheduling incident arrival event.
    """
    count = 1
    while count <= incident.index.max() :
        yield env.timeout(incident.loc[count,'arint'])
        env.process(call_arrival(
            env=env, count=count,
            time=incident.loc[count,'inc_time'],
            incident_type_id=incident.loc[count,'inc_type'],
            location=incident.loc[count,'location'],
            network=network,
            incident_type = incident_type,
            dact=incident.loc[count,'dact']))
        count +=1 

