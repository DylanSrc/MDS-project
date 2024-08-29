from obspy import read
import numpy as np
import os
from datetime import datetime, timedelta

#This algorithm aims at modifying obvious outliers, particularly this algorithm create groups which contain 10000 numbers respectively. Then calculate the
#average value of this group, data with absolute value exceeds 5 times as the average will be setted as 0
def clean_mseed_data_by_threshold(input_file):
    print(f"Reading data from {input_file}")
    stream = read(input_file)  
    for trace in stream:
        data = trace.data
        print(f"Starting threshold cleaning for {len(data)} data points...")

        interval = 10000
        for start in range(0, len(data), interval):
            
            end = min(start + interval, len(data))
            window = data[start:end]

            # The threshold to modify outliers
            threshold = np.sum(np.abs(window)) / 2000

            # check outliers
            for i in range(start, end):
                if np.abs(data[i]) > threshold:
                    data[i] = 0  # set the value of outliers

        print(f"Finished processing, writing back data to {input_file}")
        trace.data = data  

    stream.write(input_file, format='MSEED')  

def process_all_files(folder_path):
    start_date = datetime(2024, 2, 8)
    end_date = datetime(2024, 5, 18)
    current_date = start_date
    file_paths = []

    while current_date <= end_date:
        filename = f"{current_date.strftime('%Y-%m-%d')}_AM.R50D6..Z.mseed"
        filepath = os.path.join(folder_path, filename)
        if os.path.exists(filepath):
            file_paths.append(filepath)
        current_date += timedelta(days=1)

    total_files = len(file_paths)

    for idx, file_path in enumerate(file_paths, 1):
        print(f"Processing file {idx} of {total_files}: {file_path}")
        clean_mseed_data_by_threshold(file_path)
        print(f"{idx} out of {total_files} is refined")

if __name__ == "__main__":
    folder_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6'
    process_all_files(folder_path)
