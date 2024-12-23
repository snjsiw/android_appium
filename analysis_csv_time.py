import pandas as pd
import pymysql
import numpy as np

# 定义协议与端口的映射关系
protocol_port_mapping = {
    ('TCP', 443): 'DoH',
    ('TCP', 853): 'DoT',
    ('UDP', 853): 'DoQ',
    ('UDP', 443): 'DoH3',
    ('TCP', 80): 'HTTP',
}

# 数据库配置
db_config = {
    'host': "150.109.100.62",
    'user': "root",
    'password': "Zm.1575098153",
    'database': "mobile",
    'port': 3306
}

# 创建数据库连接
connection = pymysql.connect(
    host=db_config['host'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database'],
    port=db_config['port'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 加载CSV文件
df = pd.read_csv('csv/1.csv')

# 移除“应用”列中包含 "root" 的行
df_filtered = df[~df['应用'].str.contains('Root', na=False)]
# 使用 fillna() 替换 NaN 为 None
df_filtered = df_filtered.replace({np.nan: None})

# 创建原表的SQL语句
create_table_query = """
CREATE TABLE IF NOT EXISTS analysis_csv_5 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(255),
    protocol VARCHAR(50),
    resolver_info TEXT,
    resolver_ip VARCHAR(50),
    compliance_status VARCHAR(10)
);
"""

# 执行原表表创建
with connection.cursor() as cursor:
    cursor.execute(create_table_query)
connection.commit()

# 处理每一行数据，并插入到数据库（原功能）
insert_query = """
INSERT INTO analysis_csv_5 (app_name, protocol, resolver_info, resolver_ip, compliance_status)
VALUES (%s, %s, %s, %s, %s);
"""

# 创建新的表用于存储“移动应用”和“域名解析协议”
create_new_table_query = """
CREATE TABLE IF NOT EXISTS analysis_csv_2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(255),
    protocol VARCHAR(50)
);
"""

# 执行新表创建
with connection.cursor() as cursor:
    cursor.execute(create_new_table_query)
connection.commit()

# 新表的插入语句
insert_new_table_query = """
INSERT INTO analysis_csv_2 (app_name, protocol)
VALUES (%s, %s);
"""

try:
    with connection.cursor() as cursor:
        for index, row in df_filtered.iterrows():
            app_name = row['应用']  # 移动应用
            protocol = 'TCP' if row['IP协议'] == 6 else 'UDP'  # 根据IP协议判断TCP或UDP
            port = row['目标端口']  # 使用目标端口进行判断
            info = row['信息']  # 域名解析器地址信息

            # 如果“信息”列为空，使用原始协议，域名解析器地址提取“目标IP”
            if pd.isna(info) or info == '':
                domain_protocol = protocol  # 使用原始协议
                resolver_ip = row['目标IP']  # 使用目标IP
            else:
                # 如果“信息”列不为空，使用映射后的协议
                domain_protocol = protocol_port_mapping.get((protocol, port), protocol)  # 映射协议，找不到映射则使用原始协议

                # 判断域名解析器地址是源IP还是目标IP
                if (protocol, port) in protocol_port_mapping:
                    resolver_ip = row['目标IP']  # 如果协议和端口匹配，使用目标IP
                else:
                    resolver_ip = row['源IP']  # 如果协议和端口不匹配，使用源IP

            # 是否合规统一填为"合规"
            compliant_status = "合规"

            # 插入当前行到原始表
            cursor.execute(insert_query, (app_name, domain_protocol, info, resolver_ip, compliant_status))

            # 插入当前行到新的简化表，仅包含应用和协议
            cursor.execute(insert_new_table_query, (app_name, domain_protocol))

        # 提交所有插入操作
        connection.commit()

finally:
    # 关闭数据库连接
    connection.close()

print("数据已插入两个数据库表。")
