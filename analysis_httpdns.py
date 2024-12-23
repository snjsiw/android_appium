import pandas as pd
import pymysql

# 加载CSV文件
file_path = 'C:/Users/lenovo/Desktop/android_appium/httpdns.csv'  # 请确认文件路径
df = pd.read_csv(file_path)

# 分割 '移动应用' 列中的应用名称（以顿号分隔）
df['移动应用'] = df['移动应用'].str.split('、')

# 使用 explode 函数将应用名称展开为多行
df = df.explode('移动应用')

# 选择所需的列，并重命名列以符合需求
df_result = df[['移动应用', 'domain/stamp', '运营商', 'IP']].copy()
df_result.columns = ['移动应用', '私有协议DNS解析器', '运营商', '私有协议DNS解析器地址']

# 添加 '解析结果准确性' 列，并设置为 '100%'
df_result['解析结果准确性'] = '100%'

# 保存结果到新CSV文件
output_path = 'C:/Users/lenovo/Desktop/android_appium/processed_httpdns.csv'
df_result.to_csv(output_path, index=False)

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

# 创建新的表用于存储处理后的数据
create_table_query = """
CREATE TABLE IF NOT EXISTS processed_httpdns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(255),
    private_dns_resolver VARCHAR(255),
    operator VARCHAR(255),
    private_dns_resolver_address VARCHAR(255),
    accuracy VARCHAR(10)
);
"""

# 执行表创建
with connection.cursor() as cursor:
    cursor.execute(create_table_query)
connection.commit()

# 插入数据到新的表
insert_query = """
INSERT INTO processed_httpdns (app_name, private_dns_resolver, operator, private_dns_resolver_address, accuracy)
VALUES (%s, %s, %s, %s, %s);
"""

# 插入数据到数据库
try:
    with connection.cursor() as cursor:
        for index, row in df_result.iterrows():
            cursor.execute(insert_query, (
                row['移动应用'],
                row['私有协议DNS解析器'],
                row['运营商'],
                row['私有协议DNS解析器地址'],
                row['解析结果准确性']
            ))

        # 提交所有插入操作
        connection.commit()

finally:
    # 关闭数据库连接
    connection.close()

print("数据已成功插入数据库。")
