import os
import pymysql
import pandas as pd
from scapy.all import rdpcap, Raw
from scapy.layers.dns import DNS
from scapy.layers.inet import TCP, UDP, IP

class PCAPAnalyzer:
    def __init__(self, db_config, pcap_directory, doh_resolver_file, protocol_directory='protocol'):
        self.db_config = db_config
        self.pcap_directory = pcap_directory
        self.doh_resolver_ips = pd.read_csv(doh_resolver_file)['ip'].tolist()
        self.protocol_port_mapping = {
            # 原有协议映射
        }
        self.db_connection = None
        self.protocol_directory = protocol_directory
        os.makedirs(self.protocol_directory, exist_ok=True)  # 确保协议目录存在

    def connect_to_db(self):
        """建立数据库连接"""
        self.db_connection = pymysql.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            port=int(self.db_config['port']),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected to the database.")

    def create_table(self):
        """创建数据库表"""
        table_creation_query = """
        CREATE TABLE IF NOT EXISTS pcap_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            app_name VARCHAR(255),
            protocol VARCHAR(50),
            source_ip VARCHAR(50),
            source_port INT,
            destination_ip VARCHAR(50),
            destination_port INT,
            query TEXT,
            response TEXT,
            answer TEXT,
            length INT
        );
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(table_creation_query)
            self.db_connection.commit()
        print("Table 'pcap_analysis' ensured.")

    def get_latest_pcap_file(self):
        """获取指定目录中时间最新的 pcap 文件"""
        pcap_files = [f for f in os.listdir(self.pcap_directory) if f.endswith('.pcap')]
        if not pcap_files:
            print("No pcap files found in the directory.")
            return None
        latest_file = max(pcap_files, key=lambda f: os.path.getmtime(os.path.join(self.pcap_directory, f)))
        return os.path.join(self.pcap_directory, latest_file)

    def analyze_pcap(self):
        """分析指定目录中最新的PCAP文件"""
        latest_pcap = self.get_latest_pcap_file()
        if latest_pcap is None:
            return

        app_name = os.path.splitext(os.path.basename(latest_pcap))[0]
        packets = rdpcap(latest_pcap)

        # 创建协议文件字典
        protocol_files = {}

        # 限制分析的包数量
        packet_count = min(len(packets), 3000)

        for packet in packets[:packet_count]:  # 仅分析前3000个包
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst

                if TCP in packet or UDP in packet:
                    transport_layer = packet[TCP] if TCP in packet else packet[UDP]
                    src_port = transport_layer.sport
                    dst_port = transport_layer.dport

                    # 默认协议为最高层协议
                    original_protocol = packet.lastlayer().name if packet.lastlayer() else 'Unknown'
                    protocol = original_protocol

                    # 检查协议映射并更新协议名称
                    if (
                            (transport_layer.name, src_port) in self.protocol_port_mapping and
                            src_ip in self.doh_resolver_ips
                    ):
                        protocol = self.protocol_port_mapping[(transport_layer.name, src_port)]
                    elif (
                            (transport_layer.name, dst_port) in self.protocol_port_mapping and
                            dst_ip in self.doh_resolver_ips
                    ):
                        protocol = self.protocol_port_mapping[(transport_layer.name, dst_port)]

                    # 处理 HTTP 流量 (通常是 80 端口)
                    if src_port == 80 or dst_port == 80:
                        protocol = 'HTTP'
                    elif Raw in packet:
                        raw_data = packet[Raw].load.decode('utf-8', errors='ignore')
                        # 如果 Raw 数据包含 HTTP 请求特征
                        if 'HTTP' in raw_data or 'GET' in raw_data or 'POST' in raw_data:
                            protocol = 'HTTP'
                        # 如果 Raw 数据符合 TLS 握手标志
                        elif raw_data[:2] == b'\x16\x03' and (src_port == 443 or dst_port == 443):
                            protocol = 'TLS'
                        else:
                            protocol = 'TCP'  # 将其他未识别的 Raw 数据标记为 TCP

                    # 检查 QUIC 数据包
                    if UDP in packet and (dst_port == 443 or src_port == 443):
                        if Raw in packet and b'QUIC' in packet[Raw].load:
                            protocol = 'QUIC'

                    # 处理 DNS 特定字段
                    query, response, answer = 'N/A', 'N/A', 'N/A'
                    if packet.haslayer(DNS):
                        dns_layer = packet[DNS]
                        if dns_layer.qr == 0 and dns_layer.qd:
                            query = dns_layer.qd.qname.decode() if dns_layer.qd.qname else 'N/A'
                        if dns_layer.qr == 1:
                            answers = []
                            if hasattr(dns_layer, 'an') and dns_layer.an:
                                for i in range(dns_layer.ancount):
                                    answer_rr = dns_layer.an[i]
                                    answers.append(answer_rr.rrname.decode() if answer_rr.rrname else 'N/A')
                                    if hasattr(answer_rr, 'rdata'):
                                        answer = answer_rr.rdata if isinstance(answer_rr.rdata, str) else repr(
                                            answer_rr.rdata)
                            response = ', '.join(answers) if answers else 'N/A'

                    # 计算数据包长度
                    packet_length = len(packet)

                    # 打印分析出的数据包信息到屏幕上
                    output_line = f"APP Name: {app_name}, Protocol: {protocol}, Source IP: {src_ip}, Source Port: {src_port}, " \
                                  f"Destination IP: {dst_ip}, Destination Port: {dst_port}, Query: {query}, " \
                                  f"Response: {response}, Answer: {answer}, Length: {packet_length}\n"

                    # 将结果写入对应的协议文件
                    if protocol not in protocol_files:
                        protocol_files[protocol] = open(os.path.join(self.protocol_directory, f"{protocol}.txt"), 'a')

                    protocol_files[protocol].write(output_line)
                    print(f"Wrote to {protocol}.txt: {output_line.strip()}")
                    # 立即将数据包插入数据库
                    self.insert_into_db(app_name, protocol, src_ip, src_port, dst_ip, dst_port, query, response, answer,
                                        packet_length)

                    # 输出结果到屏幕
                    print(output_line.strip())

        # 关闭所有打开的协议文件
        for f in protocol_files.values():
            f.close()

    def insert_into_db(self, app_name, protocol, src_ip, src_port, dst_ip, dst_port, query, response, answer, packet_length):
        """将分析结果实时插入数据库"""
        insert_query = """
        INSERT INTO pcap_analysis 
        (app_name, protocol, source_ip, source_port, destination_ip, destination_port, query, response, answer, length)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = (app_name, protocol, src_ip, src_port, dst_ip, dst_port, query, response, answer, packet_length)

        with self.db_connection.cursor() as cursor:
            cursor.execute(insert_query, data)
            self.db_connection.commit()

    def close_db_connection(self):
        """关闭数据库连接"""
        if self.db_connection:
            self.db_connection.close()
        print("Database connection closed.")

# 使用封装的类
if __name__ == "__main__":
    db_config = {
        'host': "150.109.100.62",
        'user': "root",
        'password': "Zm.1575098153",
        'database': "mobile",
        'port': "3306"
    }

    pcap_directory = 'TEST'
    doh_resolver_file = './config/doh_resolver_ip_full.csv'
    protocol_directory = 'protocol'

    # 实例化 PCAPAnalyzer 类
    analyzer = PCAPAnalyzer(db_config, pcap_directory, doh_resolver_file, protocol_directory)

    # 连接数据库并创建表
    analyzer.connect_to_db()
    analyzer.create_table()

    # 实时分析最新的 PCAP 并逐条插入数据，同时打印到屏幕
    analyzer.analyze_pcap()
    # analyzer.analyze_all_pcaps()
    # 关闭数据库连接
    analyzer.close_db_connection()
