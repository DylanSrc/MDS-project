import matplotlib.pyplot as plt
from obspy import read

# 指定MSEED文件的路径
file_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6\2024-02-15_AM.R50D6..Z.mseed'  # 请将这里的your_file_path.mseed替换为实际的文件路径

    # 读取MSEED文件
stream = read(file_path)

    # 绘制波形图
stream.plot()