import numpy as np
import pandas as pd
from obspy import read
from datetime import datetime, timedelta
import os

def read_and_process_mseed(infile):
    stream = read(infile)
    daily_data = []
    for trace in stream:
        daily_data.extend(trace.data)
    return daily_data

def split_into_groups(data, num_groups=240):
    group_size = len(data) // num_groups
    groups = [data[i * group_size:(i + 1) * group_size] for i in range(num_groups)]
    return groups

def process_groups(groups):
    max_avg = 0
    max_group = None
    processed_groups = []
    for group in groups:
        abs_avg = np.mean(np.abs(group))
        processed_group = [0 if np.abs(x) > 10 * abs_avg else x for x in group]
        processed_groups.append(processed_group)
        group_avg = np.mean(processed_group)
        if group_avg > max_avg:
            max_avg = group_avg
            max_group = processed_group
    return processed_groups, max_group, max_avg

def calculate_standard_deviation(groups):
    all_values = [x for group in groups for x in group]
    std_dev = np.std(all_values)
    return std_dev

def write_to_excel(results, output_file='results.xlsx'):
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
        std_dev_df = pd.DataFrame(results['std_dev'], columns=['Date', 'Standard Deviation'])
        max_avg_df = pd.DataFrame(results['max_avg'], columns=['Date', 'Time Period', 'Max Average'])
        
        std_dev_df.to_excel(writer, sheet_name='Standard Deviation', index=False)
        max_avg_df.to_excel(writer, sheet_name='Max Average', index=False)

if __name__ == "__main__":
    folder_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6'  # 修改为包含所有MSEED文件的文件夹路径
    files = [f for f in os.listdir(folder_path) if f.endswith('.mseed')]
    
    results = {'std_dev': [], 'max_avg': []}

    for infile in sorted(files):
        full_path = os.path.join(folder_path, infile)
        file_date = datetime.strptime(infile.split('_')[0], "%Y-%m-%d").date()

        
        daily_data = read_and_process_mseed(full_path)
        groups = split_into_groups(daily_data)
        processed_groups, max_group, max_avg = process_groups(groups)
        std_dev = calculate_standard_deviation(processed_groups)

        
        max_index = processed_groups.index(max_group)
        start_time = (file_date + timedelta(minutes=max_index * 10)).strftime('%Y-%m-%d %H:%M')
        end_time = (file_date + timedelta(minutes=(max_index + 1) * 10)).strftime('%Y-%m-%d %H:%M')

       
        print(f"{start_time}-{end_time} time period has the maximum amplitude with value: {max_avg}, the standard deviation for the day is: {std_dev}")

       
        results['std_dev'].append([file_date, std_dev])
        results['max_avg'].append([file_date, f"{start_time}-{end_time}", max_avg])
    
    
    write_to_excel(results)
