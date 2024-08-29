import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 文件路径
data_folder = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable'

# 读取Excel文件中的数据
average_data = pd.read_excel(rf'{data_folder}\aggregated_data.xlsx', sheet_name='Daily Averages')
weather_data = pd.read_excel(rf'{data_folder}\Durham activity calendar.xlsx', sheet_name='Weather')
average_data['Date'] = pd.to_datetime(average_data['Date'])
weather_data['Date'] = pd.to_datetime(weather_data['Date'])

# 合并数据
combined_data = pd.merge(average_data, weather_data, on='Date')

# 箱线图（Box Plot）
plt.figure(figsize=(12, 6))
sns.boxplot(x='Weather', y='Daily Average (nm/s)', data=combined_data)
plt.title('Daily Average Amplitude by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('Daily Average Amplitude (nm/s)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(rf'{data_folder}\weather_vs_amplitude_box.png')
plt.show()

# 点图（Dot Plot）
plt.figure(figsize=(12, 6))
sns.stripplot(x='Weather', y='Daily Average (nm/s)', data=combined_data, jitter=True)
plt.title('Daily Average Amplitude by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('Daily Average Amplitude (nm/s)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(rf'{data_folder}\weather_vs_amplitude_dot.png')
plt.show()

# 折线图（Line Plot）
plt.figure(figsize=(12, 6))
sns.lineplot(x='Date', y='Daily Average (nm/s)', hue='Weather', data=combined_data)
plt.title('Daily Average Amplitude Over Time by Weather Condition')
plt.xlabel('Date')
plt.ylabel('Daily Average Amplitude (nm/s)')
plt.legend(title='Weather Condition')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(rf'{data_folder}\weather_vs_amplitude_line.png')
plt.show()

# 小提琴图（Violin Plot）
plt.figure(figsize=(12, 6))
sns.violinplot(x='Weather', y='Daily Average (nm/s)', data=combined_data)
plt.title('Daily Average Amplitude by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('Daily Average Amplitude (nm/s)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(rf'{data_folder}\weather_vs_amplitude_violin.png')
plt.show()

# 散点图（Scatter Plot）
plt.figure(figsize=(12, 6))
sns.scatterplot(x='Weather', y='Daily Average (nm/s)', data=combined_data)
plt.title('Daily Average Amplitude by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('Daily Average Amplitude (nm/s)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(rf'{data_folder}\weather_vs_amplitude_scatter.png')
plt.show()


#***********
data_folder = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable'

# 读取Excel文件中的数据
six_hour_data = pd.read_excel(rf'{data_folder}\aggregated_data.xlsx', sheet_name='Six-Hour Averages')
weather_data = pd.read_excel(rf'{data_folder}\Durham activty calendar.xlsx', sheet_name='Weather')

# 查看 Six-Hour Averages 视图的列名
print(six_hour_data.columns)

# 将 Date 列转换为 datetime 类型
six_hour_data['Date'] = pd.to_datetime(six_hour_data['Date'])
weather_data['Date'] = pd.to_datetime(weather_data['Date'])

# 筛选出 "midnight" 时间段的数据
midnight_data = six_hour_data[six_hour_data['Period'] == 'midnight']

# 合并数据
combined_data = pd.merge(midnight_data, weather_data, on='Date')

# 绘制箱线图
plt.figure(figsize=(12, 6))
sns.boxplot(x='Weather', y='Six-Hour Average (nm/s)', data=combined_data)
plt.title('0-6 AM Amplitude by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('0-6 AM Average Amplitude (nm/s)')
plt.xticks(rotation=45)
plt.tight_layout()

# 保存和展示图表
plt.savefig(rf'{data_folder}\weather_vs_amplitude_0_6am_box.png')
plt.show()