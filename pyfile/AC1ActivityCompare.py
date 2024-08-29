import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Data address
minute_data_path = 'C:/Users/84278/Desktop/Project of Master Data science/Dissertation/infoTable/aggregated_data.xlsx'
activity_data_path = 'C:/Users/84278/Desktop/Project of Master Data science/Dissertation/infoTable/Durham activity calendar.xlsx'

minute_data = pd.read_excel(minute_data_path, sheet_name='Minute Averages')
strikes_data = pd.read_excel(activity_data_path, sheet_name='Strikes')
holidays_data = pd.read_excel(activity_data_path, sheet_name='national holiday')

# This function is to convert date to correct format
def convert_date(date_str):
    try:
        if pd.isna(date_str):
            return None, None
        if '-' in date_str:
            start_date_str, end_date_str = date_str.split('-')
            start_date = pd.to_datetime(f'2024-{start_date_str.strip()}', format='%Y-%m.%d')
            end_date = pd.to_datetime(f'2024-{end_date_str.strip()}', format='%Y-%m.%d')
            return start_date, end_date
        else:
            single_date = pd.to_datetime(f'2024-{date_str.strip()}', format='%Y-%m.%d')
            return single_date, single_date
    except Exception as e:
        print(f"Error converting date: {date_str}, error: {e}")
        return None, None

strikes_data['Date'] = strikes_data['Date'].astype(str)
holidays_data['Date'] = holidays_data['Date'].astype(str)


strikes_data['Start Date'], strikes_data['End Date'] = zip(*strikes_data['Date'].apply(convert_date))
holidays_data['Start Date'], holidays_data['End Date'] = zip(*holidays_data['Date'].apply(convert_date))

# This function is to deal with outliers to make sure they are not to unrealistic
def filter_outliers(data, column='Minute Averages', max_iterations=1000):
    period_data = data.copy()
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
        if new_value < lower_bound:
            new_value = median_value
        period_data.at[idx, column] = new_value
    

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
        period_data.at[idx, column] = new_value
    
    return period_data


minute_data['Timestamp'] = pd.to_datetime(minute_data['Date'].astype(str) + ' ' + minute_data['Time'].astype(str))
minute_data.set_index('Timestamp', inplace=True)

# This function is to plot
def plot_seismic_data(minute_data, activities, activity_label):
    plt.figure(figsize=(12, 6))
    
    for _, row in activities.iterrows():
        start_date, end_date = row['Start Date'], row['End Date']
        plt.axvspan(start_date, end_date, color='red', alpha=0.3, label=activity_label if 'label_shown' not in locals() else None)
        locals()['label_shown'] = True

    plt.plot(minute_data.index, minute_data['Minute Averages'], label='Minute Averages', linewidth=0.5)
    plt.axhline(y=minute_data['Minute Averages'].max(), color='blue', linestyle='--', linewidth=1, label='Max Amplitude')
    plt.plot(minute_data['Minute Averages'].rolling(window=60).mean(), label='Rolling Mean', color='orange', linewidth=1)

    plt.xlabel('Date and Time')
    plt.ylabel('Minute Average Amplitude (nm/s)')
    plt.title('Seismic Wave Amplitude Variation Over Time')
    plt.legend()
    plt.show()


def plot_detailed_strikes(minute_data, strikes_data):
    for _, row in strikes_data.iterrows():
        start_date, end_date = row['Start Date'], row['End Date']
        plot_data = minute_data[start_date:end_date]
        plt.figure(figsize=(12, 6))
        plt.plot(plot_data.index, plot_data['Minute Averages'], label='Minute Averages', linewidth=0.5)
        plt.axhline(y=minute_data['Minute Averages'].max(), color='blue', linestyle='--', linewidth=1, label='Max Amplitude')
        plt.plot(plot_data['Minute Averages'].rolling(window=60).mean(), label='Rolling Mean', color='orange', linewidth=1)
        plt.xlabel('Date and Time')
        plt.ylabel('Minute Average Amplitude (nm/s)')
        plt.title(f'Seismic Wave Amplitude During Strike: {row["Name"]}')
        plt.legend()
        plt.show()


minute_data = filter_outliers(minute_data)


plot_seismic_data(minute_data, strikes_data, 'Strikes')
plot_seismic_data(minute_data, holidays_data, 'Holidays')


plot_detailed_strikes(minute_data, strikes_data)
