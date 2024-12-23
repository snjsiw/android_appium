import pandas as pd
import pymysql
import numpy as np

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

# 删除 "已发送字节数" 及其后面的所有列，包括“已发送字节数”列本身
if '已发送字节数' in df.columns:
    df = df.loc[:, :'已发送字节数'].drop(columns=['已发送字节数'])

# 使用 fillna() 替换 NaN 为 None
df = df.replace({np.nan: None})

# 创建表的SQL语句
create_table_query = """
CREATE TABLE IF NOT EXISTS analysis_app (
    id INT AUTO_INCREMENT PRIMARY KEY,
    应用 VARCHAR(255),
    IP协议 VARCHAR(50),
    源IP VARCHAR(50),
    目标IP VARCHAR(50),
    源端口 INT,
    目标端口 INT,
    信息 TEXT
);
"""

# 执行表创建
with connection.cursor() as cursor:
    cursor.execute(create_table_query)
connection.commit()

# 处理每一行数据，并插入到数据库
insert_query = """
INSERT INTO analysis_app (应用, IP协议, 源IP, 目标IP, 源端口, 目标端口, 信息)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

try:
    with connection.cursor() as cursor:
        for index, row in df.iterrows():
            # 插入当前行到数据库
            cursor.execute(insert_query, (
                row['应用'],
                row['IP协议'],
                row['源IP'],
                row['目标IP'],
                row['源端口'],
                row['目标端口'],
                row['信息']
            ))

        # 提交所有插入操作
        connection.commit()

finally:
    # 关闭数据库连接
    connection.close()

print("数据已逐行插入数据库。")
