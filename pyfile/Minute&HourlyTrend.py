import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read file, here is the address of
hourly_data_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'

hourly_data = pd.read_excel(hourly_data_path, sheet_name='Hourly Averages')

hourly_data['Timestamp'] = pd.to_datetime(hourly_data['Date'].astype(str) + ' ' + hourly_data['Hour'].astype(str) + ':00:00')

def replace_outliers_hour(df, column, window=120, max_iterations=1000):
    df = df.copy()
    for i in range(0, len(df), window):
        period_data = df.iloc[i:i+window]
        if len(period_data) == 0:
            continue
        Q1 = period_data[column].quantile(0.25)
        Q3 = period_data[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 2 * IQR
        upper_bound = Q3 + 2 * IQR

        low_outliers = period_data[period_data[column] < lower_bound]
        for idx in low_outliers.index:
            new_value = period_data.at[idx, column]
            iterations = 0
            while new_value < lower_bound and iterations < max_iterations:
                median_value = period_data[column].median()
                M = new_value - median_value
                new_value = M / 2 + median_value
                iterations += 1
            if new_value >= lower_bound:
                df.at[idx, column] = new_value

        high_outliers = period_data[period_data[column] > upper_bound]
        for idx in high_outliers.index:
            new_value = period_data.at[idx, column]
            iterations = 0
            while new_value > upper_bound and iterations < max_iterations:
                median_value = period_data[column].median()
                M = new_value - median_value
                new_value = M / 2 + median_value
                iterations += 1
            if new_value <= upper_bound:
                df.at[idx, column] = new_value

    return df

hourly_data_cleaned = replace_outliers_hour(hourly_data, 'Hourly Averages')

hourly_data_cleaned = hourly_data_cleaned.dropna()

plt.figure(figsize=(14, 8))
plt.plot(hourly_data_cleaned['Timestamp'], hourly_data_cleaned['Hourly Averages'], label='Hourly Averages', color='black', linewidth=1)

plt.xlabel('Date and Time')
plt.ylabel('Hourly Average Amplitude (nm/s)')
plt.title('Seismic Wave Amplitude Variation Over Time')

plt.axhline(y=hourly_data_cleaned['Hourly Averages'].max(), color='blue', linestyle='--', linewidth=1.5, label='Max Amplitude')

plt.plot(hourly_data_cleaned['Timestamp'], hourly_data_cleaned['Hourly Averages'].rolling(window=120, min_periods=1).mean(), color='orange', linewidth=1.5, label='Rolling Mean')

plt.legend(loc='upper right')
plt.grid(True)
plt.tight_layout()

plt.savefig(r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\seismic_wave_amplitude_variation_stylish.png')
plt.show()

##***********************************
#Now this is minutely Trend
minute_data_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'
minute_data = pd.read_excel(minute_data_path, sheet_name='Minute Averages')


minute_data['Timestamp'] = pd.to_datetime(minute_data['Date'].astype(str) + ' ' + minute_data['Time'].astype(str))


def replace_outliers_min(df, column, window=360, max_iterations=1000):
    df = df.copy()
    for i in range(0, len(df), window):
        period_data = df.iloc[i:i+window]
        if len(period_data) == 0:
            continue
        
        
        non_zero_data = period_data[period_data[column] != 0]
        median_value = non_zero_data[column].median()
        
        
        period_data.loc[period_data[column] == 0, column] = median_value
        
        Q1 = period_data[column].quantile(0.25)
        Q3 = period_data[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        low_outliers = period_data[period_data[column] < lower_bound]
        for idx in low_outliers.index:
            new_value = period_data.at[idx, column]
            iterations = 0
            while new_value < lower_bound and iterations < max_iterations:
                median_value = period_data[column].median()
                M = new_value - median_value
                new_value = M / 2 + median_value
                iterations += 1
            if new_value < lower_bound:
                new_value = median_value
            df.at[idx, column] = new_value

        high_outliers = period_data[period_data[column] > upper_bound]
        for idx in high_outliers.index:
            new_value = period_data.at[idx, column]
            iterations = 0
            while new_value > upper_bound and iterations < max_iterations:
                median_value = period_data[column].median()
                M = new_value - median_value
                new_value = M / 2 + median_value
                iterations += 1
            if new_value > upper_bound:
                new_value = median_value
            df.at[idx, column] = new_value

    return df


minute_data_cleaned = replace_outliers_min(minute_data, 'Minute Averages')


minute_data_cleaned = minute_data_cleaned.dropna()


plt.figure(figsize=(14, 8))
plt.plot(minute_data_cleaned['Timestamp'], minute_data_cleaned['Minute Averages'], label='Minute Averages', color='black', linewidth=0.2)

plt.xlabel('Date and Time')
plt.ylabel('Minute Average Amplitude (nm/s)')
plt.title('Seismic Wave Amplitude Variation Over Time')

plt.axhline(y=minute_data_cleaned['Minute Averages'].max(), color='blue', linestyle='--', linewidth=1.5, label='Max Amplitude')

plt.plot(minute_data_cleaned['Timestamp'], minute_data_cleaned['Minute Averages'].rolling(window=360, min_periods=1).mean(), color='orange', linewidth=1.5, label='Rolling Mean')
plt.legend(loc='upper right')
plt.grid(True)
plt.tight_layout()
plt.savefig(r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\seismic_wave_minute_variation.png')
plt.show()