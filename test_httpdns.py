import requests

# 常见的测试域名
domains = [
    "www.google.com",
    "www.facebook.com",
    "www.youtube.com",
    "www.baidu.com",
    "www.amazon.com",
    "www.wikipedia.org"
]

# 提供的测试 IP 地址
ips = [
    "106.74.15.134",
    "150.109.100.62",
    "172.234.92.95",
    "203.6.233.160"
]

# 阿里云请求 URL 模板
aliyun_urls = [
    "http://203.107.1.1/100000/d?host={domain}",
    "http://203.107.1.33/100000/d?host={domain}&ip={ip}",
    "http://203.107.1.1/100000/d?host={domain}&ip={ip}&query=4,6",
    "http://203.107.1.1/100000/resolve?host={domain1},{domain2}&ip={ip1},{ip2}"
]

# 网宿请求 URL
wangsu_urls = [
    "http://118.184.178.238/?ws_domain={domain}&ws_cli_IP={ip}&ws_ret_type=json"
]

# 腾讯请求 URL 模板
tencent_urls = [
    "https://119.29.29.99/d?dn={domain}&token=813959707",
    "https://119.29.29.99/d?dn={domain}&token=813959707&ttl=1",
    "https://119.29.29.99/d?dn={domain}&token=813959707&clientip=1&ip={ip}&ttl=1",
    "https://119.29.29.99/d?dn={domain1},{domain2}&token=813959707&clientip=1&ip={ip}&ttl=1"
]

# 发送请求并检查响应
def check_dns_service(url_templates, domains, ips, service_name):
    print(f"\nChecking {service_name} DNS Service...\n")
    for url_template in url_templates:
        # 替换模板中的占位符
        for domain in domains:
            for ip in ips:
                # 如果 URL 模板中有多个域名或 IP 占位符，选择两个不同的域名和两个不同的 IP 进行替换
                url = url_template.format(
                    domain=domain,
                    ip=ip,
                    domain1=domains[0],
                    domain2=domains[1],
                    ip1=ips[0],
                    ip2=ips[1]
                )
                try:
                    response = requests.get(url, timeout=5)
                    print(f"Request URL: {url}")
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json() if response.headers.get('Content-Type') == 'application/json' else response.text[:200]}")
                except requests.RequestException as e:
                    print(f"Request to {url} failed: {e}")

# 调用不同的服务请求
check_dns_service(aliyun_urls, domains, ips, "Aliyun")
check_dns_service(wangsu_urls, domains, ips, "Wangsu")
check_dns_service(tencent_urls, domains, ips, "Tencent")
