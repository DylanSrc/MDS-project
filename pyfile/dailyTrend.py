import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from scipy.optimize import curve_fit

# 读取Excel数据
file_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'

# 读取 Minute Averages 工作表
df = pd.read_excel(file_path, sheet_name='Minute Averages')

# 将日期和时间合并为一个 datetime 对象
df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))

# 添加额外的时间列
df['Weekday'] = df['DateTime'].dt.weekday
df['Hour'] = df['DateTime'].dt.hour
df['Minute'] = df['DateTime'].dt.minute

# 过滤出工作日（星期一到星期五）4:00-22:00的数据
daily_df = df.loc[(df['Weekday'] < 5) & (df['Hour'] >= 4) & (df['Hour'] < 22)].copy()

# 提取周数
daily_df['Week'] = daily_df['DateTime'].dt.isocalendar().week

# ------------------------- 图一 -------------------------
# 计算每一分钟的中位数震动幅度（图一）
grouped = daily_df.groupby(['Hour', 'Minute'])['Minute Averages']
median_by_minute = grouped.apply(np.median).reset_index()

# 绘制图一
plt.figure(figsize=(14, 8))

time_labels = [f"{int(h):02}:{int(m):02}" for h, m in zip(median_by_minute['Hour'], median_by_minute['Minute'])]

# 只标注每个整点
hours = median_by_minute['Hour'].unique()
xticks = [f"{hour:02}:00" for hour in hours]
xtick_positions = [time_labels.index(label) for label in xticks]

plt.plot(time_labels, median_by_minute['Minute Averages'], marker='o')

# 在9点和17点添加红色竖向虚线
plt.axvline(x=xtick_positions[5], color='red', linestyle='--', label='9:00 AM')
plt.axvline(x=xtick_positions[13], color='red', linestyle='--', label='5:00 PM')

plt.title('Median of Minute Averages Over Day (4:00-22:00)')
plt.xlabel('Time')
plt.ylabel('Median Minute Amplitude (nm/s)')
plt.xticks(ticks=xtick_positions, labels=xticks, rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 保存图一的结果
output_file_1 = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\median_trend_analysis_day_results.xlsx'
with pd.ExcelWriter(output_file_1) as writer:
    median_by_minute.to_excel(writer, sheet_name='Median By Minute', index=False)

# ------------------------- 图二 -------------------------
# 计算每周每一分钟的中位数
grouped_weekly = daily_df.groupby(['Week', 'Hour', 'Minute'])['Minute Averages']
weekly_median = grouped_weekly.apply(np.median).reset_index()

# 计算所有周中每一分钟中位数的中位数（图二）
overall_median_by_minute = weekly_median.groupby(['Hour', 'Minute'])['Minute Averages'].median().reset_index()

# 绘制图二
plt.figure(figsize=(14, 8))

time_labels = [f"{int(h):02}:{int(m):02}" for h, m in zip(overall_median_by_minute['Hour'], overall_median_by_minute['Minute'])]

# 只标注每个整点
hours = overall_median_by_minute['Hour'].unique()
xticks = [f"{hour:02}:00" for hour in hours]
xtick_positions = [time_labels.index(label) for label in xticks]

plt.plot(time_labels, overall_median_by_minute['Minute Averages'], marker='o')

# 在9点和17点添加红色竖向虚线
plt.axvline(x=xtick_positions[5], color='red', linestyle='--', label='9:00 AM')
plt.axvline(x=xtick_positions[13], color='red', linestyle='--', label='5:00 PM')

plt.title('Median of Weekly Median Minute Averages Over Day (4:00-22:00)')
plt.xlabel('Time')
plt.ylabel('Median of Weekly Median Minute Amplitude (nm/s)')
plt.xticks(ticks=xtick_positions, labels=xticks, rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 保存图二的结果
output_file_2 = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\overall_median_trend_analysis_day_results.xlsx'
with pd.ExcelWriter(output_file_2) as writer:
    overall_median_by_minute.to_excel(writer, sheet_name='Overall Median By Minute', index=False)



# 读取Excel数据
file_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'

# 读取 Minute Averages 工作表
df = pd.read_excel(file_path, sheet_name='Minute Averages')

# 将日期和时间合并为一个 datetime 对象
df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))

# 添加额外的时间列
df['Weekday'] = df['DateTime'].dt.weekday
df['Hour'] = df['DateTime'].dt.hour
df['Minute'] = df['DateTime'].dt.minute

# 过滤出工作日（星期一到星期五）4:00-22:00的数据
daily_df = df.loc[(df['Weekday'] < 5) & (df['Hour'] >= 4) & (df['Hour'] < 22)].copy()

# 提取周数
daily_df['Week'] = daily_df['DateTime'].dt.isocalendar().week

# 计算每周每一分钟的中位数
grouped_weekly = daily_df.groupby(['Week', 'Hour', 'Minute'])['Minute Averages']
weekly_median = grouped_weekly.apply(np.median).reset_index()

# 计算所有周中每一分钟中位数的中位数
overall_median_by_minute = weekly_median.groupby(['Hour', 'Minute'])['Minute Averages'].median().reset_index()

# ------------------------- 正弦函数拟合 -------------------------
# 定义正弦函数模型
def sinusoidal_model(t, A, T, phi, C):
    return A * np.sin(2 * np.pi * t / T + phi) + C

# 时间（小时）
X = overall_median_by_minute['Hour'] + overall_median_by_minute['Minute'] / 60
y = overall_median_by_minute['Minute Averages']

# 初始猜测参数
initial_guess = [np.std(y), 24, 0, np.mean(y)]  # 振幅，周期为24小时，相位，常数偏移量

# 拟合正弦函数
params, params_covariance = curve_fit(sinusoidal_model, X, y, p0=initial_guess)

# 打印拟合参数
A_fit, T_fit, phi_fit, C_fit = params
print(f"Fitted parameters:\nAmplitude (A): {A_fit}\nPeriod (T): {T_fit}\nPhase (phi): {phi_fit}\nOffset (C): {C_fit}")

# 计算拟合的R²值
y_pred = sinusoidal_model(X, *params)
residuals = y - y_pred
ss_res = np.sum(residuals**2)
ss_tot = np.sum((y - np.mean(y))**2)
r_squared_sinusoidal = 1 - (ss_res / ss_tot)

print(f"R-squared for Sinusoidal Fit: {r_squared_sinusoidal}")

# ------------------------- 每小时平均值、标准差计算及数据打印 -------------------------
# 计算每小时的平均值和标准差
hourly_stats = overall_median_by_minute.groupby('Hour')['Minute Averages'].agg(['mean', 'std'])

# 打印每个小时的平均值、标准差及与上一个小时的差异
print("\nHourly Analysis (Mean and Standard Deviation):")
previous_mean = None
previous_std = None

for hour in range(4, 22):
    current_mean = hourly_stats.loc[hour, 'mean']
    current_std = hourly_stats.loc[hour, 'std']
    
    if previous_mean is not None:
        mean_diff = current_mean - previous_mean
        std_diff = current_std - previous_std
    else:
        mean_diff = "NA"
        std_diff = "NA"
    
    print(f"\nHour: {hour:02d}:00")
    print(f"Mean: {current_mean:.3f} (Difference from previous hour: {mean_diff})")
    print(f"Standard Deviation: {current_std:.3f} (Difference from previous hour: {std_diff})")
    
    previous_mean = current_mean
    previous_std = current_std

# ------------------------- 数据可视化 -------------------------
# 可视化正弦函数拟合曲线
plt.figure(figsize=(14, 8))
plt.scatter(X, y, color='blue', label='Data Points', s=10)
plt.plot(X, y_pred, color='red', label=f'Sinusoidal Fit (R² = {r_squared_sinusoidal:.3f})')

# 在9点和17点添加红色竖向虚线
plt.axvline(x=9, color='red', linestyle='--', label='9:00 AM')
plt.axvline(x=17, color='red', linestyle='--', label='5:00 PM')

# 设置x轴刻度为每2小时一个，并显示具体时间
xticks = np.arange(4, 23, 2)  # 从4点到22点每2小时一个刻度
xticklabels = [f'{int(hour):02}:00' for hour in xticks]
plt.xticks(ticks=xticks, labels=xticklabels)

plt.title('Sinusoidal Fit of Median Minute Averages Over Day (4:00-22:00)')
plt.xlabel('Time (Hour)')
plt.ylabel('Median Minute Amplitude (nm/s)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
