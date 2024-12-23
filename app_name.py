import os
import random

# 定义文件夹路径
folder_path = r"D:\porn_PCAP"

# 获取文件夹中的文件列表
files = os.listdir(folder_path)

# 对于大小相等的文件，添加一定量的随机数据
for i, file_name in enumerate(files):
    file_path = os.path.join(folder_path, file_name)

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 随机生成100到500字节的随机数据
    extra_bytes = random.randint(100, 500)
    random_data = bytes([random.randint(0, 255) for _ in range(extra_bytes)])

    # 在文件末尾添加随机数据
    with open(file_path, 'ab') as f:
        f.write(random_data)

print("文件大小已修改，每个文件增加了随机字节。")
