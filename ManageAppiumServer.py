import subprocess
import os

from Common.handle_path import appium_logs_dir

class ManageAppiumServer:
    """
    appium desktop通过命令行启动appium服务。
    不同平台上安装的appium，默认的appium服务路径不一样。
    初始化时，设置appium服务启动路径
    再根据给定的端口号启动appium
    """

    def __init__(self,appium_server_apth):
        self.server_apth = appium_server_apth

    # 启动appium server服务
    def start_appium_server(self,port=4723):
        appium_log_path = os.path.join(appium_logs_dir,"appium_server_{0}.log".format(port))
        command = "node {0} -p {1} -g {2} " \
                  "--session-override " \
                  "--local-timezone " \
                  "--log-timestamp & ".format(self.server_apth, port, appium_log_path)
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()

    # 关闭appium服务
    @classmethod
    def stop_appium(cls,pc,post_num=4723):
        '''关闭appium服务'''
        if pc.upper() == 'WIN':
            p = os.popen(f'netstat  -aon|findstr {post_num}')
            p0 = p.read().strip()
            if p0 != '' and 'LISTENING' in p0:
                p1 = int(p0.split('LISTENING')[1].strip()[0:4])  # 获取进程号
                os.popen(f'taskkill /F /PID {p1}')  # 结束进程
                print('appium server已结束')
        elif pc.upper() == 'MAC':
            p = os.popen(f'lsof -i tcp:{post_num}')
            p0 = p.read()
            if p0.strip() != '':
                p1 = int(p0.split('\n')[1].split()[1])  # 获取进程号
                os.popen(f'kill {p1}')  # 结束进程
                print('appium server已结束')

