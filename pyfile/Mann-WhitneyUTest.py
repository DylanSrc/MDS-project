import pandas as pd
import scipy.stats as stats

# read data
six_hour_data_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'
weather_data_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\Durham activity calendar.xlsx'

six_hour_data = pd.read_excel(six_hour_data_path, sheet_name='Six-Hour Averages')
weather_data = pd.read_excel(weather_data_path, sheet_name='Weather')

# combine data for testing use
combined_data = pd.merge(six_hour_data, weather_data, on='Date')
all_data = combined_data


results = {}
weathers = ['Light Rain', 'Overcast', 'Sunny', 'Heavy Rain']

for i in range(len(weathers)):
    for j in range(i + 1, len(weathers)):
        weather1 = weathers[i]
        weather2 = weathers[j]
        data1 = all_data[all_data['Weather'] == weather1]['Six-Hour Average (nm/s)']
        data2 = all_data[all_data['Weather'] == weather2]['Six-Hour Average (nm/s)']
        if len(data1) > 0 and len(data2) > 0:  
            t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False)
            results[f'{weather1} vs {weather2}'] = p_val
        else:
            results[f'{weather1} vs {weather2}'] = 'Insufficient data'

# Display the significance
for key, p_val in results.items():
    print(f'{key}: p-value = {p_val}')
