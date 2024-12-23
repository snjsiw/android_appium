import os
import pymysql
import pandas as pd
from scapy.all import rdpcap, Raw
from scapy.layers.dns import DNS
from scapy.layers.inet import TCP, UDP, IP

class PCAPAnalyzer:
    def __init__(self, db_config, pcap_directory, doh_resolver_file):
        self.db_config = db_config
        self.pcap_directory = pcap_directory
        self.doh_resolver_ips = pd.read_csv(doh_resolver_file)['ip'].tolist()
        self.protocol_port_mapping = {
            ('TCP', 443): 'DoH',
            ('TCP', 853): 'DoT',
            ('UDP', 853): 'DoQ',
            ('UDP', 443): 'DoH3',
            ('TCP', 80): 'HTTP',
            ('TCP', 21): 'FTP',
            ('TCP', 25): 'SMTP',
            ('TCP', 22): 'SSH',
            ('TCP', 23): 'Telnet',
            ('UDP', 123): 'NTP',
            ('TCP', 3389): 'RDP',
            ('TCP', 5060): 'SIP',
            ('UDP', 5060): 'SIP',
            ('TCP', 554): 'RTSP',
            ('UDP', 443): 'QUIC',
            ('TCP', 67): 'DHCP',
            ('TCP', 69): 'TFTP',
            ('TCP', 500): 'IPSec',
            ('UDP', 500): 'IPSec',
        }
        self.db_connection = None

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
        CREATE TABLE IF NOT EXISTS pcap_Compliance (
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

    def insert_into_db(self, record):
        """立刻将分析结果插入数据库"""
        insert_query = """
        INSERT INTO pcap_Compliance 
        (app_name, protocol, source_ip, source_port, destination_ip, destination_port, query, response, answer, length)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(insert_query, record)
            self.db_connection.commit()

    def analyze_pcaps(self):
        """分析目录中的所有 PCAP 文件"""
        pcap_files = [f for f in os.listdir(self.pcap_directory) if f.endswith('.pcap')]
        if not pcap_files:
            print("No pcap files found in the directory.")
            return

        for pcap_file in pcap_files:
            pcap_path = os.path.join(self.pcap_directory, pcap_file)
            app_name = os.path.splitext(pcap_file)[0]

            try:
                packets = rdpcap(pcap_path)
            except Exception as e:
                print(f"Error reading {pcap_file}: {e}")
                continue

            insert_data = []  # 用于收集每个 PCAP 文件的记录
            count = 0

            for packet in packets:
                if count >= 2000:  # 每个PCAP最多分析2000行
                    break
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

                        # 处理 HTTP 流量 (通常是 80 端口)
                        if src_port == 80 or dst_port == 80:
                            protocol = 'HTTP'
                        elif Raw in packet:
                            raw_data = packet[Raw].load.decode('utf-8', errors='ignore')
                            if 'HTTP' in raw_data or 'GET' in raw_data or 'POST' in raw_data:
                                protocol = 'HTTP'

                        # 检查 QUIC 流量
                        if UDP in packet and (dst_port == 443 or src_port == 443):
                            if Raw in packet:
                                raw_data = packet[Raw].load
                                if b'QUIC' in raw_data:
                                    protocol = 'QUIC'

                        # 检查 TLS 流量
                        if Raw in packet and (src_port == 443 or dst_port == 443):
                            try:
                                raw_data = packet[Raw].load
                                if raw_data[:2] == b'\x16\x03':
                                    protocol = 'TLS'
                                else:
                                    protocol = 'TCP'
                            except Exception:
                                protocol = 'TCP'

                        # 修改协议名称
                        if ((transport_layer.name, src_port) in self.protocol_port_mapping and
                                src_ip in self.doh_resolver_ips):
                            protocol = self.protocol_port_mapping[(transport_layer.name, src_port)]
                        elif ((transport_layer.name, dst_port) in self.protocol_port_mapping and
                              dst_ip in self.doh_resolver_ips):
                            protocol = self.protocol_port_mapping[(transport_layer.name, dst_port)]

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

                        # 将数据包信息添加到本次 PCAP 的记录中
                        insert_data.append((app_name, protocol, src_ip, src_port, dst_ip, dst_port, query, response,
                                            answer, packet_length))
                        count += 1

            # 分析完 2000 条记录后一次性插入数据库
            if insert_data:
                self.batch_insert_into_db(insert_data)
                print(f"Finished analyzing {pcap_file}, processed {count} packets, records inserted into database.")

    def batch_insert_into_db(self, data):
        """一次性批量插入数据库"""
        insert_query = """
        INSERT INTO pcap_Compliance 
        (app_name, protocol, source_ip, source_port, destination_ip, destination_port, query, response, answer, length)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        with self.db_connection.cursor() as cursor:
            cursor.executemany(insert_query, data)
            self.db_connection.commit()
        print(f"Inserted {len(data)} records into the database.")

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

    pcap_directory = 'F:/PCAP/PCAP'
    doh_resolver_file = './config/doh_resolver_ip_full.csv'

    # 实例化 PCAPAnalyzer 类
    analyzer = PCAPAnalyzer(db_config, pcap_directory, doh_resolver_file)

    # 连接数据库并创建表
    analyzer.connect_to_db()
    analyzer.create_table()

    # 分析所有 PCAP 文件并立刻插入数据库
    analyzer.analyze_pcaps()

    # 关闭数据库连接
    analyzer.close_db_connection()
