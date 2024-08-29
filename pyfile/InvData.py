import datetime
import os
import glob
import time

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42  # to edit text in Illustrator
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
import tqdm
import warnings

from obspy import UTCDateTime, read
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.client import FDSNNoDataException
from obspy.signal import PPSD


# DATE RANGE TO DOWNLOAD AND ANALYSE DATA FROM
start = UTCDateTime("2024-04-16")
end = UTCDateTime("2024-05-15")

datelist = pd.date_range(start.datetime, min(end, UTCDateTime()).datetime, freq="D")
DOWNLOAD=True #set to True to download data (or False)
# Create list of stations to download ( in format: network, station, provider)
# data_provider can be:"http://eida.bgs.ac.uk" /"IRIS"/"ORFEUS"/"RASPISHAKE"/'http://fdsnws.raspberryshakedata.org' etc. *****NOTE RAPISHAKE CURRENTLY NOT WORKING - SERVER DOWN*******
Stats2download=[]
Stats2download.append(['AM','R50D6','https://data.raspberryshake.org']) #2

# Loop through each station in list
for line in Stats2download:
    network = line[0]
    station = line[1]
    data_provider = line[2]

    location = "*"
    channel = "*Z*" # Channel to analyse vertical=Z)
    dataset = network + "." + station # Choose a name for your dataset
    time_zone = "GMT"
    sitedesc = network + "." + station

    cur_dir = os.getcwd()
    print(network, station, data_provider, location, channel, dataset, time_zone, sitedesc)

    nslc = "{}.{}.{}.{}".format(network, station, location, channel)
    # Make sure that wildcard characters are not in nslc
    nslc = nslc.replace("*", "").replace("?", "")
    pbar = tqdm.tqdm(datelist)

    c = Client('https://data.raspberryshake.org')

    # Loop through each day requested
    for day in pbar:
        datestr = day.strftime("%Y-%m-%d")

        # Set data file name structure
        resp_filename = "{}_{}_{}.xml".format(datestr, nslc, 'response')
        
        # If response file doesn't already exist
        if not os.path.isfile(resp_filename):
            pbar.set_description("Fetching %s" % resp_filename)
            try:
                # Download instrument response file
                resp = c.get_stations(UTCDateTime(day), network=network, station=station, location=location, channel=channel, level="response")
                # Write to file and save
                resp.write(resp_filename, format='STATIONXML')
                print('Saved:', resp_filename)
            except FDSNNoDataException:
                pbar.set_description("No data on FDSN server for %s" % resp_filename)
            except Exception as e:
                print("An error occurs, stopping for a while:", e)
                time.sleep(5)