import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# Load the data from the "Hourly Averages" sheet
file_path = 'C:/Users/84278/Desktop/Project of Master Data science/Dissertation/infoTable/modified_aggregated_data.xlsx'
hourly_data = pd.read_excel(file_path, sheet_name='Hourly Averages')

# Create an hourly timestamp by assuming each row represents the next hour
hourly_data['Timestamp'] = pd.to_datetime(hourly_data['Date']) + pd.to_timedelta(hourly_data.groupby('Date').cumcount(), unit='h')
hourly_data.set_index('Timestamp', inplace=True)

# Filter data to only include working hours (9 AM to 5 PM)
working_hours_data = hourly_data.between_time('09:00', '17:00')

# Remove outliers using IQR
def remove_outliers(df, column_name):
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]

working_hours_data = remove_outliers(working_hours_data, 'Hourly Averages')

# Add a column indicating whether the day is a weekday or weekend
working_hours_data['DayOfWeek'] = working_hours_data.index.dayofweek
working_hours_data['DayType'] = np.where(working_hours_data['DayOfWeek'] < 5, 'Weekday', 'Weekend')

# Define the term time and vacation time
term_start = pd.to_datetime('2024-01-08')
term_end = pd.to_datetime('2024-03-15')
vacation_start = pd.to_datetime('2024-03-16')
vacation_end = pd.to_datetime('2024-04-21')

# Filter for term time weekdays and vacation weekdays
term_time_data = working_hours_data[(working_hours_data.index.date >= term_start.date()) & 
                                    (working_hours_data.index.date <= term_end.date()) & 
                                    (working_hours_data['DayType'] == 'Weekday')]

vacation_time_data = working_hours_data[(working_hours_data.index.date >= vacation_start.date()) & 
                                        (working_hours_data.index.date <= vacation_end.date()) & 
                                        (working_hours_data['DayType'] == 'Weekday')]

# Calculate means
term_time_mean = term_time_data['Hourly Averages'].mean()
vacation_time_mean = vacation_time_data['Hourly Averages'].mean()

# Print the results
print(f"Term Time Weekday Mean: {term_time_mean}")
print(f"Vacation Time Weekday Mean: {vacation_time_mean}")

# Perform statistical tests
t_stat, p_value = stats.ttest_ind(term_time_data['Hourly Averages'], vacation_time_data['Hourly Averages'], equal_var=False)
cohens_d = (term_time_mean - vacation_time_mean) / np.sqrt((np.std(term_time_data['Hourly Averages']) ** 2 + np.std(vacation_time_data['Hourly Averages']) ** 2) / 2)

print(f"T-Statistic: {t_stat}, P-Value: {p_value}")
print(f"Cohen's d: {cohens_d}")

# Visualization
plt.figure(figsize=(12, 6))
sns.kdeplot(term_time_data['Hourly Averages'], label='Term Time Weekday', shade=True, color='blue')
sns.kdeplot(vacation_time_data['Hourly Averages'], label='Vacation Time Weekday', shade=True, color='red')
plt.title('Seismic Activity Density Estimation: Term Time vs. Vacation (Weekday Hourly Averages)')
plt.xlabel('Hourly Averages')
plt.ylabel('Density')
plt.legend()
plt.grid(True)
plt.show()

# Generate overlapping histogram (distribution comparison)
plt.figure(figsize=(12, 6))
sns.histplot(term_time_data['Hourly Averages'], label='Term Time Weekday', kde=True, color='blue', stat='density', bins=30, alpha=0.5)
sns.histplot(vacation_time_data['Hourly Averages'], label='Vacation Time Weekday', kde=True, color='red', stat='density', bins=30, alpha=0.5)
plt.title('Seismic Activity Distribution: Term Time vs. Vacation (Weekday Hourly Averages)')
plt.xlabel('Hourly Averages')
plt.ylabel('Density')
plt.legend()
plt.grid(True)
plt.show()
