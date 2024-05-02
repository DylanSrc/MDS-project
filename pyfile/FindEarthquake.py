#Script to locate earthquakes in reported global catalogues of a set size (bettween 0-10 magnitude) within a set distance of a location (e.g. the place where you station is.

import obspy
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import URL_MAPPINGS
from obspy import UTCDateTime

#Where to dowload earthquake catalogue from
fromwhere="IRIS"
 
sta_latitude=54.76576577
sta_longitude=-1.561623997

# Earthquakes to look for event parameters
start_time='2023-01-01' #within this time frame
end_time='2024-01-01' #within this time frame
radmin = 0  # Minimum radius (in epicentral degrees) for teleseismic earthquakes from your statlocation
radmax = 90  # Maximum radius (further distances - up to 180, interact with the core-mantle boundary)
minmag = 5.5  # Minumum magnitude of quake
maxmag = 8.5  # Maximum magnitude of quake


# load IRIS client
irisclient = Client(fromwhere)

#put start/end time in right format
starttime = UTCDateTime(start_time)
endtime = UTCDateTime(end_time)

# Find all suitable events in earthquake catalogue
cat = irisclient.get_events(
    latitude=sta_latitude,
    longitude=sta_longitude,
    minradius=radmin,
    maxradius=radmax,
    starttime=starttime,
    endtime=endtime,
    minmagnitude=minmag)
print('No. Identified Earthquakes', len(cat))

#view catalogue
cat.plot()

#print out list of all events
print(cat.__str__(print_all=True))
