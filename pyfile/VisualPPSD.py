from obspy import read
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.core.inventory import read_inventory


#Select a trace with the desired station/channel combination:here i have downloaded the file, pls change to the add of your files
file_path = r"C:\Users\84278\Desktop\codefile\C++\AM.R50D6\2024-02-08_AM.R50D6..Z.mseed"
resp_path = r"C:\Users\84278\Desktop\codefile\C++\AM.R50D6\2024-02-08_AM.R50D6..Z_response.xml"

st = read(file_path)
for tr in st:
    print(tr.id)
tr = st.select(id="AM.R50D6.00.EHZ")[0]

#Read the mseed file downloaded from the official website
inv = read_inventory(resp_path)
ppsd = PPSD(tr.stats, metadata=inv)

#add data (either trace or stream objects) to the ppsd estimate.
ppsd.add(st)


#check what time ranges are represented in the ppsd estimate.
print(ppsd.times_processed[:2])

print("number of psd segments:", len(ppsd.times_processed))

#Adding the same stream again will do nothing, because the ppsd object makes sure that no overlapping data segments go into the ppsd estimate.
ppsd.add(st)
print("number of psd segments:", len(ppsd.times_processed))

#This method to add additional information from other files
file_path = r"C:\Users\84278\Desktop\codefile\C++\AM.R50D6\2024-02-09_AM.R50D6..Z.mseed"
st = read(file_path)
ppsd.add(st)

#now let's start to plot ppsd
ppsd.plot()

#If you want to save the plot docu, just activate these code
#ppsd.plot("/tmp/ppsd.png")  
#ppsd.plot("/tmp/ppsd.pdf")  

#A (for each frequency bin) cumulative version of the histogram can also be visualized:
ppsd.plot(cumulative=True)

#To use the colormap used by PQLX 
from obspy.imaging.cm import pqlx
ppsd.plot(cmap=pqlx)

#Follow with Time series of psd values
ppsd.plot_temporal([0.1, 1, 10])

#Spectrogram-like plots can also be done
ppsd.plot_spectrogram()

#Plotting Spectrograms
st.merge(method=1)
for tr in st:
    if not ppsd.add(tr):
        print(f"Skipping overlapping data at {tr.stats.starttime}")
st.spectrogram(log=True, title=f'AM.R50D6 {str(st[0].stats.starttime)}')