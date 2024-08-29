import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 读取数据
hourly_data_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'

# 读取 "Hourly Averages" sheet 中的数据
hourly_data = pd.read_excel(hourly_data_path, sheet_name='Hourly Averages')

# 创建一个新的 Timestamp 列
hourly_data['Timestamp'] = pd.to_datetime(hourly_data['Date'].astype(str) + ' ' + hourly_data['Hour'].astype(str) + ':00:00')

# 定义处理极值点的函数
def replace_outliers(df, column, window=120, max_iterations=1000):
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

# 处理极值点
hourly_data_cleaned = replace_outliers(hourly_data, 'Hourly Averages')

# 检查并处理缺失值
hourly_data_cleaned = hourly_data_cleaned.dropna()

# 绘制地震波动变化趋势图
plt.figure(figsize=(14, 8))
plt.plot(hourly_data_cleaned['Timestamp'], hourly_data_cleaned['Hourly Averages'], label='Hourly Averages')

plt.xlabel('Date and Time')
plt.ylabel('Hourly Average Amplitude (nm/s)')
plt.title('Seismic Wave Amplitude Variation Over Time')
plt.legend(loc='upper right')
plt.grid(True)
plt.tight_layout()

# 保存图表
plt.savefig(r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\seismic_wave_amplitude_variation_continuous.png')
plt.show()
