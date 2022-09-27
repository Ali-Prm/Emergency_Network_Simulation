from collections import namedtuple

# Generating the station class containing node id and resources in each station.
## It also stores the availability status, operation time, and utilization parameters for each vehicle in stations. 

Station = namedtuple('Station',
                     ['zone_num', 'vehicles', 'availability','operation_time', 'utilization'])