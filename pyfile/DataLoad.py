#Download seismic data in .mseed format in folder named after station.  One file per day. Sampling rate usually 100sps

import datetime
import os
import shutil
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



#DATA TO DOWNLOAD
#no, site, net.stat, data_server, start_date, end_date, info-online
#1, Durham Uni Raspberry Shake, AM.R50D6, RAPISHAKE, 2023-06-20, 2599-12-31, https://dataview.raspberryshake.org/#/AM/R50D6/00/EHZ
#2, - Edmundbuyers national monitorring, GB.EDMD, IRIS, 2011-10-01, 2599-12-31, https://earthquakes.bgs.ac.uk/data/station_book/stationbook_edmd.html





#DATE RANGE TO DOWNLOAD AND ANALYSE DATA FROM
#set as "yyyy-mm-dd" based on operating times - will download one .mseed file per day - may be large data set if you do a long time period!
start = UTCDateTime("2024-03-15")
end = UTCDateTime("2024-04-15")


datelist = pd.date_range(start.datetime, min(end, UTCDateTime()).datetime, freq="D")
DOWNLOAD=True #set to True to download data (or False)
#Create list of stations to download ( in format: network, station, provider)
#data_provider can be:"http://eida.bgs.ac.uk" /"IRIS"/"ORFEUS"/"RASPISHAKE"/'http://fdsnws.raspberryshakedata.org' etc. *****NOTE RAPISHAKE CURRENTLY NOT WORKING - SERVER DOWN*******
Stats2download=[]
Stats2download.append(['AM','R50D6','https://data.raspberryshake.org']) #2


#loop through each station in list
for line in Stats2download:
    network=line[0]
    station=line[1]
    data_provider=line[2]
   
    location = "*"
    channel = "*Z*" #channel to analyse vertical=Z)
    dataset = network+"."+station #choose a name for your dataset
    time_zone = "GMT"
    sitedesc = network+"."+station


    cur_dir=os.getcwd()
    print(network,station,data_provider,location,channel,dataset,time_zone,sitedesc)

    nslc = "{}.{}.{}.{}".format(network, station, location, channel)
    # make sure that wildcard characters are not in nslc
    nslc = nslc.replace("*", "").replace("?", "")
    pbar = tqdm.tqdm(datelist)

    c = Client(data_provider)
    #download instrument response file
    resp = c.get_stations(UTCDateTime(start), network=network, station=station,location=location,channel=channel, level="response")
    print('GETTING RESP')

    #if download parameter set to true download this data
    if DOWNLOAD:
        #load provider

        #loop through each day requested
        for day in pbar:
            datestr = day.strftime("%Y-%m-%d")

            c = Client(data_provider)
            #download instrument response file
            resp = c.get_stations(UTCDateTime(day), network=network, station=station,location=location,channel=channel, level="response")
            print(resp)
            
            #set data file name struture
            fn = "{}_{}.mseed".format(datestr, nslc)
            
            #if data file doesn't already exist
            if day != UTCDateTime().datetime and os.path.isfile(fn):
                continue
            else:
                pbar.set_description("Fetching %s" % fn)
                try: 
                    #download data
                    st = c.get_waveforms(network, station, location, channel,
                                          UTCDateTime(day)-1801, UTCDateTime(day)+86400+1801,
                                          attach_response=True)
                    try:    
                        print('mergining')                
                        st.merge()
                        for tr in st:
                            if isinstance(tr.data, np.ma.masked_array):
                                tr.data = tr.data.filled()
                    except:
                        continue
                except FDSNNoDataException:
                    pbar.set_description("No data on FDSN server for %s" % fn)
                    continue
                except Exception as e:
                    print("An error occurs, stopping for a while:", e)
                    time.sleep(5)
                #write to file and save
                try:
                    st.write(fn)
                except:
                    continue



        #makedir for seismic data to go in
        cur_dir=os.getcwd()
        if not os.path.exists(cur_dir+'/'+dataset):
        	os.mkdir(cur_dir+'/'+dataset)
        #move downloaded mseed seismic data to this location
        for file2mv in glob.glob("*"+dataset+'*.mseed'):
            shutil.move(file2mv, cur_dir+'/'+dataset+'/.')
            
        print(cur_dir)



