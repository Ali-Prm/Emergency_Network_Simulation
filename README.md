# A DES Model For Simulation The Operation of a Emergency Service System.
A DES Model is implemented from scratch for fire service operation. 


## How to Run:
First, run the following in your terminal to add project root directory to python search path:
```
export PYTHONPATH=${PWD}
```

Then, run the main project script by:
```
python src/run.py
```

## Problem Statement:
Emergency service systems perform critical tasks daily, and they are responsible for saving people's lives and assets. The location-allocation problem has been studied from different perspectives; however, many gaps are left unchecked. Numerous sources of uncertainties are involved, such as the random nature of incident occurrence, uncertainties in the transportation network, and a so-called congestion problem, which accounts for the unavailability of emergency units.<br>
This simulation model tries to address and quantify these sources of uncertainties, and it is a tool that can act as a decision support system for decision-makers by which they can clearly evaluate the effectiveness of decisions and modifications. Additionally, this model can be used alongside an optimization model in a simulation-optimization approach that possibly leads to a better solution than a static optimization model. <br>
Additional information is provided in the `slides.pdf` file in the docs directory. 


# Model Desctription:
The model overview is as follows:
![Alt text](docs/model_overview.png?raw=true "Model Overview")

The discrete events of the simulation model are:
1. Incident Arrival Event: Events are generated when `incident_process` function is called. 
2. Vehicles' Arrival Event: After the incident's occurrence, the nearest available vehicles are assigned to the incident.
3. Service Event: After the required vehicles arrive, the service event gets started. 
4. Vehicles' Return Event: After the service time is passed, vehicles return to their stations. 
![Alt text](docs/model_flowchart.png?raw=true "Model Flowchart")

The fundamental assumptions are as follows:
1. Incidents: Three types of fire incidents are considered
- Type-1: (Secondary Fire incidents) Human lives are not at the stack, and they usually occur in open spaces. 
- Type-2: (Primary Fire incidents that do not need a ladder) They occur in houses and workplaces with one to five floors. 
- Type-2: (Primary Fire incidents that need a ladder) They occur in houses and workplaces with more than six floors. 
![Alt text](docs/incident_assumption.png?raw=true "Incident assumption")

2. Vehicle: Three types of vehicles are considered
- Type-1: (Heading vehicle) The most basic and smallest vehicles that serve every incident.
- Type-2: (Tanker vehicle) It carries water and is sent to primary incidents.
- Type-3: (Ladder) It is needed for operation in highrise buildings. 
![Alt text](docs/vehicle_assumptions.png?raw=true "Incident assumption")


# Files info 
- The `experiment.ipynb` is a simulation experiment that evaluates the performance of three different resource configurations over 12 replication. 
-  The `call_arrival.py` model the steps each incident goes through. It is the heart of this simulation model and implements the logic of the model flowchart. 
-  The `incident_process.py` is a generator function that realeses the incidents into the simulation environment. 
- The `Network.py` is a class that contains essential assumptions and characteristics about the emergency system services. 
- The `zone.py` is a class that models the relationship between nodes in the network.
- The `staion.py` is a class containing the station's node id and resources and stores the resources' availability information in itself. 
- The `helper_functions_output.py` is a helper function for processing and visualizing performance parameters in the simulation experiment.
- The `data` contains the simulation experiment's data. 
- The `doc` contains the document about the model.



