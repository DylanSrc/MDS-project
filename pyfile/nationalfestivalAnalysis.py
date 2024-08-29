import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 加载地震数据
seismic_data_path = r'C:\Users\84278\Desktop\Project of Master Data science\Dissertation\infoTable\aggregated_data.xlsx'
seismic_data = pd.read_excel(seismic_data_path, sheet_name='Minute Averages')

# 修正后的事件数据，确保长度一致
events_data = {
    "Date": ["2.14", "2.16", "2.24", "2.29", "3.2", "3.3", "3.5", "3.9", "3.12", "4.1", "4.15", "4.27", "5.24", "6.14", "6.15", "7.12", "7.18", "4.2"],
    "Event": [
        "University open days", "International Women's Day", "Chinese New Year Lantern Festival", "IAS Research Showcase", 
        "High Performance Mindset Workshop", "Hina Matsuri Celebration", "Durham Inclusive Life Drawing", 
        "Gospel Choir Performance", "Welsh Tales Concert", "World Heritage Site Day", "Global Week", 
        "University open days", "Widening participation events", "Pre-offer visit days", "Widening participation events", 
        "Green Futures DEI", "Easter holiday", "University Staff Strike"
    ]
}

# 创建DataFrame并格式化日期
events_df = pd.DataFrame(events_data)
events_df['Date'] = pd.to_datetime('2024-' + events_df['Date'], format='%Y-%m.%d')

# 将地震数据的日期时间格式化
seismic_data['Date'] = pd.to_datetime(seismic_data['Date'])

# 确保没有零值影响归一化
min_value = seismic_data['Minute Averages'][seismic_data['Minute Averages'] > 0].min()

# 定义一个函数来检测事件期间地震数据的变化
def analyze_impact(event_date, seismic_data, hours_before=1, hours_after=1):
    before_event = seismic_data[(seismic_data['Date'] >= event_date - pd.Timedelta(hours=hours_before)) &
                                (seismic_data['Date'] < event_date)]
    during_event = seismic_data[(seismic_data['Date'] >= event_date) &
                                (seismic_data['Date'] < event_date + pd.Timedelta(hours=hours_after))]
    after_event = seismic_data[(seismic_data['Date'] >= event_date + pd.Timedelta(hours=hours_after)) &
                               (seismic_data['Date'] < event_date + pd.Timedelta(hours=hours_after * 2))]
    
    before_mean = before_event['Minute Averages'].mean()
    during_mean = during_event['Minute Averages'].mean()
    after_mean = after_event['Minute Averages'].mean()
    
    print(f"Event: {event_date} Before Mean: {before_mean}, During Mean: {during_mean}, After Mean: {after_mean}")
    
    return before_mean, during_mean, after_mean

# 分析每个事件的影响并绘制图表
results = []
for _, row in events_df.iterrows():
    before, during, after = analyze_impact(row['Date'], seismic_data)
    results.append([row['Date'], before, during, after])

# 将结果转换为DataFrame以便可视化
results_df = pd.DataFrame(results, columns=['Date', 'Before', 'During', 'After'])

# 绘制每个事件的影响图
plt.figure(figsize=(14, 8))
plt.plot(results_df['Date'], results_df['Before'], label='Before Event')
plt.plot(results_df['Date'], results_df['During'], label='During Event')
plt.plot(results_df['Date'], results_df['After'], label='After Event')
plt.xlabel('Date')
plt.ylabel('Seismic Activity (Minute Averages)')
plt.title('Impact of Events on Seismic Activity')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 保存分析结果
results_df.to_csv('event_seismic_analysis.csv', index=False)
