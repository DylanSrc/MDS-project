import matplotlib.pyplot as plt
from obspy import read
import numpy as np

# choose the address of your mseed file, the function of this algorithm is to select 1 in 2000 points and plot
file_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6\2024-04-16_AM.R50D6..Z.mseed'
stream = read(file_path)


earthquake_date = stream[0].stats.starttime.date  # here is the start date of seismic data

times = stream[0].times()[::2000]  
data = stream[0].data[::2000]     

# this step is to plot
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(times, data, label='Seismic Data', color='black', linewidth=0.5)

# here we can adjust trigger time
trigger_time = times[100]  
max_amplitude = max(data)
ax.axvline(x=trigger_time, color='red', linestyle='--', linewidth=2, label='Trigger at {:.4f}s'.format(trigger_time))
ax.axhline(y=max_amplitude, color='blue', linestyle='--', linewidth=2, label='Max Amplitude')


ax.set_title(f'Detected Seismic Data of {earthquake_date}')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')
ax.legend()

#This step is to adjust the canvas for observation
max_amplitude = max(data)
min_amplitude = min(data)
ax.set_ylim(min_amplitude+10000, max_amplitude)
ax.grid(True)


window_size = 50  
trend = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
trend_times = times[:len(trend)]  
ax.plot(trend_times, trend, color='#FFA07A', linewidth=0.5, label='Trend Line')

plt.tight_layout()
plt.show()
