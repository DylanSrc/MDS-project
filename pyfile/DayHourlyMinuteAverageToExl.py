import numpy as np
import pandas as pd
from obspy import read
from datetime import datetime, timedelta
import os

def read_and_group_mseed_data(infile):
    stream = read(infile)
    day_groups = {}
    six_hour_groups = {}
    hourly_groups = {}
    minute_groups = {}

    
    labels = {0: "midnight", 1: "morning", 2: "afternoon", 3: "evening"}
    #here is to set labels for daily, hourly, minute average 
    for trace in stream:
        for idx, amplitude in enumerate(trace.data):
            time = trace.stats.starttime + idx * trace.stats.delta
            day_key = time.date
            six_hour_key = time.hour // 6  
            hour_key = time.hour  
            minute_key = (time.hour, time.minute)  

            
            if day_key not in day_groups:
                day_groups[day_key] = []
            day_groups[day_key].append(amplitude)

            
            group_label = labels[six_hour_key]
            if (day_key, group_label) not in six_hour_groups:
                six_hour_groups[(day_key, group_label)] = []
            six_hour_groups[(day_key, group_label)].append(amplitude)

            
            if (day_key, hour_key) not in hourly_groups:
                hourly_groups[(day_key, hour_key)] = []
            hourly_groups[(day_key, hour_key)].append(amplitude)


            if (day_key, minute_key) not in minute_groups:
                minute_groups[(day_key, minute_key)] = []
            minute_groups[(day_key, minute_key)].append(amplitude)

    return day_groups, six_hour_groups, hourly_groups, minute_groups

def calculate_averages(groups):
    averages = {}
    for key, amplitudes in groups.items():
        averages[key] = np.average(amplitudes)
    return averages

def append_to_excel(writer, day_averages, six_hour_averages, hourly_averages, minute_averages):

    day_data = {'Date': [], 'Daily Average (nm/s)': []}
    six_hour_data = {'Date': [], 'Period': [], 'Six-Hour Average (nm/s)': []}
    hourly_data = {'Date': [], 'Hour': [], 'Hourly Average (nm/s)': []}
    minute_data = {'Date': [], 'Time': [], 'Minute Average (nm/s)': []}

    for day, avg in day_averages.items():
        day_data['Date'].append(day)
        day_data['Daily Average (nm/s)'].append(avg)
    
    for (day, period), avg in six_hour_averages.items():
        six_hour_data['Date'].append(day)
        six_hour_data['Period'].append(period)
        six_hour_data['Six-Hour Average (nm/s)'].append(avg)
    
    for (day, hour), avg in hourly_averages.items():
        hourly_data['Date'].append(day)
        hourly_data['Hour'].append(hour)
        hourly_data['Hourly Average (nm/s)'].append(avg)
    
    for (day, minute), avg in minute_averages.items():
        minute_data['Date'].append(day)
        minute_data['Time'].append(f"{minute[0]:02}:{minute[1]:02}")
        minute_data['Minute Average (nm/s)'].append(avg)
    
    day_df = pd.DataFrame(day_data)
    six_hour_df = pd.DataFrame(six_hour_data)
    hourly_df = pd.DataFrame(hourly_data)
    minute_df = pd.DataFrame(minute_data)

    # Write data into files
    day_df.to_excel(writer, sheet_name='Daily Averages', index=False, header=not writer.sheets, startrow=writer.sheets['Daily Averages'].max_row if 'Daily Averages' in writer.sheets else 0)
    six_hour_df.to_excel(writer, sheet_name='Six-Hour Averages', index=False, header=not writer.sheets, startrow=writer.sheets['Six-Hour Averages'].max_row if 'Six-Hour Averages' in writer.sheets else 0)
    hourly_df.to_excel(writer, sheet_name='Hourly Averages', index=False, header=not writer.sheets, startrow=writer.sheets['Hourly Averages'].max_row if 'Hourly Averages' in writer.sheets else 0)
    minute_df.to_excel(writer, sheet_name='Minute Averages', index=False, header=not writer.sheets, startrow=writer.sheets['Minute Averages'].max_row if 'Minute Averages' in writer.sheets else 0)

if __name__ == "__main__":
    folder_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6' 
    output_file = 'aggregated_data.xlsx'

    
    files = [f for f in os.listdir(folder_path) if f.endswith('.mseed')]
    
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
        for infile in sorted(files):
            full_path = os.path.join(folder_path, infile)
            
            day_groups, six_hour_groups, hourly_groups, minute_groups = read_and_group_mseed_data(full_path)

            
            file_date = datetime.strptime(infile.split('_')[0], "%Y-%m-%d").date()

            
            day_averages = calculate_averages(day_groups)
            filtered_day_averages = {k: v for k, v in day_averages.items() if k == file_date}

            
            six_hour_averages = calculate_averages(six_hour_groups)
            filtered_six_hour_averages = {k: v for k, v in six_hour_averages.items() if k[0] == file_date}

            
            hourly_averages = calculate_averages(hourly_groups)
            filtered_hourly_averages = {k: v for k, v in hourly_averages.items() if k[0] == file_date}

            
            minute_averages = calculate_averages(minute_groups)
            filtered_minute_averages = {k: v for k, v in minute_averages.items() if k[0] == file_date}

            
            print(f"Processing file: {infile}")
            print("Daily Averages:")
            for day, avg in filtered_day_averages.items():
                print(f"{day}: {avg} nm/s")

            print("\nSix-Hour Averages:")
            for (day, period), avg in filtered_six_hour_averages.items():
                print(f"{day} {period}: {avg} nm/s")

            print("\nHourly Averages:")
            for (day, hour), avg in filtered_hourly_averages.items():
                
                
                print(f"{day} {hour}:00: {avg} nm/s")

            print("\nMinute Averages:")
            for (day, time), avg in filtered_minute_averages.items():
                print(f"{day} {time[0]:02}:{time[1]:02}: {avg} nm/s")

            
            append_to_excel(writer, filtered_day_averages, filtered_six_hour_averages, filtered_hourly_averages, filtered_minute_averages)
