import traceback
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import asyncio  # 导入 asyncio 以支持异步任务

from auto_two import start_pcapdroid_session, operation_steps
from analysis_pcap import PCAPAnalyzer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义可操作的应用列表
app_name_list = [
    {'appName': '微信', 'appPackage': 'com.tencent.mm', 'appActivity': 'com.tencent.mm.ui.LauncherUI'},
    {'appName': '抖音', 'appPackage': 'com.ss.android.ugc.aweme', 'appActivity': 'com.ss.android.ugc.aweme.main.MainActivity'},
    {'appName': '小红书', 'appPackage': 'com.xingin.xhs', 'appActivity': 'com.xingin.xhs.activity.SplashActivity'},
    {'appName': 'QQ音乐HD', 'appPackage': 'com.tencent.qqmusicpad', 'appActivity': 'ccom.tencent.qqmusicpad.activity.MainActivity'}
]

# 配置数据库和PCAP分析目录
db_config = {
    'host': "150.109.100.62",
    'user': "root",
    'password': "Zm.1575098153",
    'database': "mobile",
    'port': "3306"
}

pcap_directory = './TEST'
doh_resolver_file = './config/doh_resolver_ip_full.csv'

# 根目录
@app.get("/")
async def root():
    return {"message": "Hello!"}

# 异步执行自动化操作的函数
async def execute_operation(app):
    try:
        driver = start_pcapdroid_session("127.0.0.1:62025")
        # 执行自动化操作
        operation_steps(app, 2)  # 传入选定的app对象

        # 操作完成后，分析PCAP文件
        print("自动化操作完成，开始分析PCAP文件...")
        analyzer = PCAPAnalyzer(db_config, pcap_directory, doh_resolver_file)
        analyzer.connect_to_db()
        analyzer.create_table()
        analyzer.analyze_pcap()  # 分析保存的PCAP文件
        analyzer.close_db_connection()
        print("PCAP文件分析完成，数据已插入数据库。")

    except Exception as e:
        traceback.print_exc()

# 定义接收appName的路由
@app.get("/operate")
async def operate_app(appName: str):
    try:
        # 在app列表中查找对应的应用
        app = next((app for app in app_name_list if app['appName'] == appName), None)
        if not app:
            raise HTTPException(status_code=404, detail="App not found")

        # 启动后台任务，执行自动化操作
        asyncio.create_task(execute_operation(app))  # 启动异步任务执行操作

        # 立即返回响应
        return {"message": f"Successfully started operation on {appName}"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

# http://127.0.0.1:8000/operate?appName=%E5%BE%AE%E4%BF%A1