import pandas as pd
import numpy as np
import datetime
from openpyxl import load_workbook
from scipy import stats
from datetime import datetime

#Step1: choose a baseline to analyze

minute_data_path = 'C:/Users/84278/Desktop/Project of Master Data science/Dissertation/infoTable/aggregated_data.xlsx'
strikes_data_path = 'C:/Users/84278/Desktop/Project of Master Data science/Dissertation/infoTable/Durham activity calendar.xlsx'


minute_data = pd.read_excel(minute_data_path, sheet_name='Minute Averages')
strikes_data = pd.read_excel(strikes_data_path, sheet_name='Strikes')


minute_data['Timestamp'] = pd.to_datetime(minute_data['Date'].astype(str) + ' ' + minute_data['Time'])


def convert_dates(date_str):
    try:
        if '-' in date_str:
            start_date, end_date = date_str.split('-')
            start_date = start_date.strip()
            end_date = end_date.strip()
        else:
            start_date = end_date = date_str.strip()
        return start_date, end_date
    except Exception as e:
        print(f"Error parsing date: {date_str}. Error: {e}")
        return None, None

strikes_data[['Start Date', 'End Date']] = strikes_data['Date'].apply(lambda x: convert_dates(x)).apply(pd.Series)

# calculate datetime by hand
from datetime import datetime, timedelta

def add_days(date_str, days):
    date_obj = datetime.strptime(date_str, "%Y/%m/%d")
    new_date = date_obj + timedelta(days=days)
    return new_date.strftime("%Y/%m/%d")

def subtract_days(date_str, days):
    date_obj = datetime.strptime(date_str, "%Y/%m/%d")
    new_date = date_obj - timedelta(days=days)
    return new_date.strftime("%Y/%m/%d")

# check baseline
def print_baseline_periods():
    for index, row in strikes_data.iterrows():
        if row['Start Date'] and row['End Date']:
            start_date = row['Start Date']
            end_date = row['End Date']
            
            baseline_pre_start = subtract_days(start_date, 4)
            baseline_pre_end = subtract_days(start_date, 1)
            baseline_post_start = add_days(end_date, 1)
            baseline_post_end = add_days(end_date, 4)
            
            print(f"Event: {row['Name']}")
            print(f"Event Date Range: {start_date} to {end_date}")
            print(f"Baseline Pre Event: {baseline_pre_start} to {baseline_pre_end}")
            print(f"Baseline Post Event: {baseline_post_start} to {baseline_post_end}")
            print()

print("Strikes Data after Date conversion:")
print(strikes_data)
print()

print_baseline_periods()


##-------
# Step2: Process minute_data and calculate statistics for baseline and event periods

# Define functions to manually process data without using pandas
def filter_data_by_date_range(data, start_date, end_date):
    filtered_data = []
    for entry in data:
        if start_date <= entry['Timestamp'] <= end_date:
            filtered_data.append(entry)
    return filtered_data

def calculate_mean(data, key):
    values = [entry[key] for entry in data]
    return sum(values) / len(values) if values else 0

def calculate_std(data, key, mean):
    values = [entry[key] for entry in data]
    variance = sum((x - mean) ** 2 for x in values) / len(values) if values else 0
    return variance ** 0.5

def calculate_variance(data, key, mean):
    values = [entry[key] for entry in data]
    return sum((x - mean) ** 2 for x in values) / len(values) if values else 0

def filter_outliers(data, column):
    values = [entry[column] for entry in data]
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 2 * IQR
    upper_bound = Q3 + 2 * IQR
    filtered_data = [entry for entry in data if lower_bound <= entry[column] <= upper_bound]
    return filtered_data

# processing minute data file
def process_minute_data(minute_data, baseline_pre_start, baseline_pre_end, baseline_post_start, baseline_post_end, start_date, end_date):
    baseline_pre_data = filter_data_by_date_range(minute_data, baseline_pre_start, baseline_pre_end)
    event_data = filter_data_by_date_range(minute_data, start_date, end_date)
    baseline_post_data = filter_data_by_date_range(minute_data, baseline_post_start, baseline_post_end)

    # 过滤极值
    baseline_pre_data = filter_outliers(baseline_pre_data, 'Minute Averages')
    event_data = filter_outliers(event_data, 'Minute Averages')
    baseline_post_data = filter_outliers(baseline_post_data, 'Minute Averages')

    baseline_pre_mean = calculate_mean(baseline_pre_data, 'Minute Averages')
    event_mean = calculate_mean(event_data, 'Minute Averages')
    baseline_post_mean = calculate_mean(baseline_post_data, 'Minute Averages')

    baseline_pre_std = calculate_std(baseline_pre_data, 'Minute Averages', baseline_pre_mean)
    event_std = calculate_std(event_data, 'Minute Averages', event_mean)
    baseline_post_std = calculate_std(baseline_post_data, 'Minute Averages', baseline_post_mean)

    baseline_pre_variance = calculate_variance(baseline_pre_data, 'Minute Averages', baseline_pre_mean)
    event_variance = calculate_variance(event_data, 'Minute Averages', event_mean)
    baseline_post_variance = calculate_variance(baseline_post_data, 'Minute Averages', baseline_post_mean)

    return {
        'Baseline Pre Mean': baseline_pre_mean,
        'Event Mean': event_mean,
        'Baseline Post Mean': baseline_post_mean,
        'Baseline Pre Std': baseline_pre_std,
        'Event Std': event_std,
        'Baseline Post Std': baseline_post_std,
        'Baseline Pre Variance': baseline_pre_variance,
        'Event Variance': event_variance,
        'Baseline Post Variance': baseline_post_variance
    }

def analyze_strike_periods():
    strike_periods = [
        {"name": "Postal Workers' Strike", "start": "2024/2/12", "end": "2024/2/16"},
        {"name": "Healthcare Workers' Strike", "start": "2024/3/15", "end": "2024/3/17"},
        {"name": "Rail Workers' Strike (RMT Union)", "start": "2024/5/8", "end": "2024/5/10"},
    ]

    for period in strike_periods:
        start_date = datetime.strptime(period['start'], "%Y/%m/%d")
        end_date = datetime.strptime(period['end'], "%Y/%m/%d")

        baseline_pre_start = start_date - timedelta(days=4)
        baseline_pre_end = start_date - timedelta(days=1)
        baseline_post_start = end_date + timedelta(days=1)
        baseline_post_end = end_date + timedelta(days=4)

        results = process_minute_data(minute_data.to_dict('records'), baseline_pre_start, baseline_pre_end, baseline_post_start, baseline_post_end, start_date, end_date)

        print(f"Event: {period['name']}")
        print(f"Baseline Pre Event: {baseline_pre_start} to {baseline_pre_end}")
        print(f"Baseline Post Event: {baseline_post_start} to {baseline_post_end}")
        print(f"Baseline Pre Mean: {results['Baseline Pre Mean']}, Std: {results['Baseline Pre Std']}, Variance: {results['Baseline Pre Variance']}")
        print(f"Event Mean: {results['Event Mean']}, Std: {results['Event Std']}, Variance: {results['Event Variance']}")
        print(f"Baseline Post Mean: {results['Baseline Post Mean']}, Std: {results['Baseline Post Std']}, Variance: {results['Baseline Post Variance']}")
        print()

analyze_strike_periods()


###Step3:
# Step3: Perform T-test to determine significance of differences

def perform_t_test(baseline_pre_data, event_data):
    # Extract the 'Minute Averages' values for each period
    baseline_pre_values = [entry['Minute Averages'] for entry in baseline_pre_data]
    event_values = [entry['Minute Averages'] for entry in event_data]
    
    # Perform T-test
    t_stat, p_value = stats.ttest_ind(baseline_pre_values, event_values, equal_var=False)
    
    return t_stat, p_value

def analyze_strike_periods_with_tests():
    strike_periods = [
        {"name": "Postal Workers' Strike", "start": "2024/2/12", "end": "2024/2/16"},
        {"name": "Healthcare Workers' Strike", "start": "2024/3/15", "end": "2024/3/17"},
        {"name": "Rail Workers' Strike (RMT Union)", "start": "2024/5/8", "end": "2024/5/10"},
    ]

    for period in strike_periods:
        start_date = datetime.strptime(period['start'], "%Y/%m/%d")
        end_date = datetime.strptime(period['end'], "%Y/%m/%d")

        baseline_pre_start = start_date - timedelta(days=4)
        baseline_pre_end = start_date - timedelta(days=1)
        baseline_post_start = end_date + timedelta(days=1)
        baseline_post_end = end_date + timedelta(days=4)

        baseline_pre_data = filter_data_by_date_range(minute_data.to_dict('records'), baseline_pre_start, baseline_pre_end)
        event_data = filter_data_by_date_range(minute_data.to_dict('records'), start_date, end_date)
        baseline_post_data = filter_data_by_date_range(minute_data.to_dict('records'), baseline_post_start, baseline_post_end)

        # 过滤极值
        baseline_pre_data = filter_outliers(baseline_pre_data, 'Minute Averages')
        event_data = filter_outliers(event_data, 'Minute Averages')
        baseline_post_data = filter_outliers(baseline_post_data, 'Minute Averages')

        baseline_pre_mean = calculate_mean(baseline_pre_data, 'Minute Averages')
        event_mean = calculate_mean(event_data, 'Minute Averages')
        baseline_post_mean = calculate_mean(baseline_post_data, 'Minute Averages')

        baseline_pre_std = calculate_std(baseline_pre_data, 'Minute Averages', baseline_pre_mean)
        event_std = calculate_std(event_data, 'Minute Averages', event_mean)
        baseline_post_std = calculate_std(baseline_post_data, 'Minute Averages', baseline_post_mean)

        baseline_pre_variance = calculate_variance(baseline_pre_data, 'Minute Averages', baseline_pre_mean)
        event_variance = calculate_variance(event_data, 'Minute Averages', event_mean)
        baseline_post_variance = calculate_variance(baseline_post_data, 'Minute Averages', baseline_post_mean)

        t_stat, p_value = perform_t_test(baseline_pre_data, event_data)
        print(f"Event: {period['name']}")
        print(f"Baseline Pre Event: {baseline_pre_start} to {baseline_pre_end}")
        print(f"Baseline Post Event: {baseline_post_start} to {baseline_post_end}")
        print(f"Baseline Pre Mean: {baseline_pre_mean}, Std: {baseline_pre_std}, Variance: {baseline_pre_variance}")
        print(f"Event Mean: {event_mean}, Std: {event_std}, Variance: {event_variance}")
        print(f"Baseline Post Mean: {baseline_post_mean}, Std: {baseline_post_std}, Variance: {baseline_post_variance}")
        print(f"T-Statistic: {t_stat}, P-Value: {p_value}")
        print()

analyze_strike_periods_with_tests()



# Step4: Calculate Cohen's d for each event to quantify the effect size of the strike on seismic activity


strike_events = [
    {'name': 'Postal Workers\' Strike', 'start_date': '2024/2/12', 'end_date': '2024/2/16'},
    {'name': 'Healthcare Workers\' Strike', 'start_date': '2024/3/15', 'end_date': '2024/3/17'},
    {'name': 'Rail Workers\' Strike (RMT Union)', 'start_date': '2024/5/8', 'end_date': '2024/5/10'}
]

def calculate_cohens_d(baseline, event):
    n1, n2 = len(baseline), len(event)
    mean1, mean2 = np.mean(baseline), np.mean(event)
    std1, std2 = np.std(baseline, ddof=1), np.std(event, ddof=1)
    
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
    cohens_d = (mean2 - mean1) / pooled_std
    
    return cohens_d

def get_data_in_range(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y/%m/%d %H:%M:%S")
    end_date = datetime.strptime(end_date_str, "%Y/%m/%d %H:%M:%S")
    return [row for idx, row in minute_data.iterrows() if start_date <= row['Timestamp'] <= end_date]

def analyze_strike_with_cohens_d():
    for event in strike_events:
        baseline_pre_start = subtract_days(event['start_date'], 4)
        baseline_pre_end = subtract_days(event['start_date'], 1)
        baseline_post_start = add_days(event['end_date'], 1)
        baseline_post_end = add_days(event['end_date'], 4)
        
        baseline_pre_data = get_data_in_range(baseline_pre_start + " 00:00:00", baseline_pre_end + " 23:59:59")
        event_data = get_data_in_range(event['start_date'] + " 00:00:00", event['end_date'] + " 23:59:59")
        baseline_post_data = get_data_in_range(baseline_post_start + " 00:00:00", baseline_post_end + " 23:59:59")
        
        baseline_pre_values = [row['Minute Averages'] for row in baseline_pre_data]
        event_values = [row['Minute Averages'] for row in event_data]
        baseline_post_values = [row['Minute Averages'] for row in baseline_post_data]
        
        cohens_d_pre_event = calculate_cohens_d(baseline_pre_values, event_values)
        cohens_d_post_event = calculate_cohens_d(baseline_post_values, event_values)
        
        print(f"Event: {event['name']}")
        print(f"Cohen's d (Baseline Pre vs. Event): {cohens_d_pre_event}")
        print(f"Cohen's d (Baseline Post vs. Event): {cohens_d_post_event}")
        print()


analyze_strike_with_cohens_d()