import time
import random
import os
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from analysis_pcap import PCAPAnalyzer
from auto_app_page import send_element, click_element, wait_element

# 启动PCAPDroid会话
# def start_pcapdroid_session(device_name):
#     options = UiAutomator2Options()
#     options.platform_name = 'Android'
#     options.device_name = '127.0.0.1:8011'
#     # options.platform_version = '12'
#     options.app_activity = 'com.emanuelef.remote_capture.activities.MainActivity'
#     options.app_package = 'com.emanuelef.remote_capture'
#     options.no_reset = True
#     options.dont_stop_app_on_reset = True  # 防止重置和关闭应用
#
#     # 初始化 WebDriver
#     return webdriver.Remote(command_executor='http://localhost:4723', options=options)
# 数据库配置
db_config = {
    'host': "150.109.100.62",
    'user': "root",
    'password': "Zm.1575098153",
    'database': "mobile",
    'port': "3306"
}

# 目标目录和 DoH 解析器文件
pcap_directory = 'C:/Users/lenovo/Desktop/android_appium/TEST'
doh_resolver_file = 'C:/Users/lenovo/Desktop/android_appium/config/doh_resolver_ip_full.csv'

# 生成 PCAPAnalyzer 实例
analyzer = PCAPAnalyzer(db_config, pcap_directory, doh_resolver_file)

def start_pcapdroid_session(device_name):
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = '127.0.0.1:62025'
    options.platform_version = '12'
    options.app_activity = 'com.emanuelef.remote_capture.activities.MainActivity'
    options.app_package = 'com.emanuelef.remote_capture'
    options.no_reset = True
    options.dont_stop_app_on_reset = True  # 防止重置和关闭应用
    # 初始化 WebDriver
    return webdriver.Remote(command_executor='http://127.0.0.1:4723', options=options)

# 随机操作页面方法
def random_click(driver):
    # 获取屏幕的宽高
    width = driver.get_window_size()['width']
    height = driver.get_window_size()['height']
    # 生成随机的点击坐标
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    # 执行点击操作
    os.system(f"adb shell input tap {x} {y}")
    # print(f"在坐标 ({x}, {y}) 进行了随机点击")


# 指定一个应用并打开，然后随机操作
def open_app_and_random_clicks(app_name,driver):
    # 强制停止应用
    os.system(f"adb shell am force-stop {app_name['appPackage']}")
    time.sleep(2)  # 等待应用停止

    print(f"正在启动应用：{app_name['appPackage']}，主活动：{app_name['appActivity']}")
    result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f"{app_name['appPackage']}/{app_name['appActivity']}"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # 等待应用加载

    # 检查启动结果
    if result.returncode != 0:
        print(f"启动应用失败，错误信息：{result.stderr.decode('utf-8')}")
        return

    # 随机点击
    for _ in range(10):  # 随机点击三次

        time.sleep(2)  # 等待一段时间再进行下一次点击     random_click(driver)

    # 强制停止应用
    os.system(f"adb shell am force-stop {app_name['appPackage']}")
    print(f"已强制停止应用：{app_name['appName']}")

# 检查开关状态
def check_and_toggle_switch(driver):
    switch_state = driver.find_element(AppiumBy.XPATH, '//android.widget.Switch[@resource-id="com.emanuelef.remote_capture:id/app_filter_switch"]')
    if switch_state.get_attribute('checked') == 'false':  # 开关是关闭的
        print("开关已关闭，正在开启开关")
        click_element(driver, (AppiumBy.XPATH, '//android.widget.Switch[@resource-id="com.emanuelef.remote_capture:id/app_filter_switch"]'), '开启目标应用Switch')
        time.sleep(2)
    else:
        print("开关已开启，正在关闭开关")
        click_element(driver, (AppiumBy.XPATH, '//android.widget.Switch[@resource-id="com.emanuelef.remote_capture:id/app_filter_switch"]'), '关闭目标应用Switch')
        time.sleep(2)
        # 再次开启开关
        click_element(driver, (AppiumBy.XPATH, '//android.widget.Switch[@resource-id="com.emanuelef.remote_capture:id/app_filter_switch"]'), '开启目标应用Switch')
        time.sleep(2)

# 执行操作步骤
def operation_steps(app,waite_time):

    driver = start_pcapdroid_session("127.0.0.1:62025")
    # 第一步:点击PCAP文件选项
    click_element(driver, (AppiumBy.XPATH,
                               '//android.widget.Spinner[@resource-id="com.emanuelef.remote_capture:id/dump_mode_spinner"]/android.widget.LinearLayout'),'PCAP文件选项')
    time.sleep(5)

    # 第二步:选择PCAP菜单选项
    click_element(driver, (AppiumBy.XPATH,
                               '//android.widget.ListView[@resource-id="com.emanuelef.remote_capture:id/select_dialog_listview"]/android.widget.LinearLayout[3]'),
                      'PCAP文件选项')
    time.sleep(5)

    # 第三步:检查并切换目标应用Switch状态
    check_and_toggle_switch(driver)

    # 第四步输入需要搜索的应用
    # send_element(driver, (AppiumBy.XPATH,
    #                       '//android.widget.AutoCompleteTextView[@resource-id="com.emanuelef.remote_capture:id/search_src_text"]'),
    #              app['appName'], '搜索应用')
    send_element(driver, (AppiumBy.XPATH,"//android.widget.EditText[@text='搜索应用']"),app['appName'], '搜索应用')
    time.sleep(5)

    # 第五步:找到应用并点击
    click_element(driver, (
    AppiumBy.XPATH, '(//android.widget.ImageView[@resource-id="com.emanuelef.remote_capture:id/app_icon"])[1]'),
                      f"{app['appName']}")
    time.sleep(5)

    # 第六步:点击启动按钮
    click_element(driver, (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="启动"]'), '启动按钮')
    time.sleep(5)

    # 第七步：修改文件名称
    file_name = wait_element(driver,
                                 (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="android:id/title"]')).text
    print(f'获取当前默认文件名称: {file_name}')
    new_file_name = file_name.replace("PCAPdroid", app['appName'])
    print(f'替换后的文件名称: {new_file_name}')
    click_element(driver, (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="android:id/title"]'))
    time.sleep(5)
    wait_element(driver, (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="android:id/title"]')).clear()
    time.sleep(5)
    send_element(driver, (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="android:id/title"]'),
                    new_file_name)
    time.sleep(5)

    # 第八步点击保存
    click_element(driver, (AppiumBy.XPATH, '//android.widget.Button[@resource-id="android:id/button1"]'), '保存')
    # click_element(driver, (AppiumBy.XPATH, "//android.widget.TextView[@text='保存']"),'保存')
    time.sleep(5)


    # 第九步：打开目标应用并执行随机点击
    open_app_and_random_clicks(app,driver)
    time.sleep(5)

    # 第十步：停止应用
    click_element(driver, (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="停止"]'), '停止')
    time.sleep(3)

    # 第十一步：停止应用后确认页面弹窗
    click_element(driver, (AppiumBy.XPATH, '//android.widget.Button[@resource-id="android:id/button3"]'), '确认')
    time.sleep(waite_time)

    # 第十二步：保存PCAP到本地
    print(new_file_name)
    os.system(f"adb pull /sdcard/{new_file_name} C:/Users/lenovo/Desktop/android_appium/TEST")
    time.sleep(5)  # 等待应用停止
    # # 连接数据库并创建表
    # analyzer.connect_to_db()
    # analyzer.create_table()
    #
    # # 立即分析刚刚下载的最新的 PCAP 文件
    # analyzer.analyze_pcap()
    #
    # # 关闭数据库连接
    # analyzer.close_db_connection()
    driver.quit()  # 关闭 WebDriver

if __name__ == '__main__':
    #填写设备名称

    driver = start_pcapdroid_session("127.0.0.1:62025")
    # 需要操作的应用名
    app_name = [
        {'appName': '微信','appPackage': 'com.tencent.mm','appActivity': 'com.tencent.mm.ui.LauncherUI'},
        {'appName': '抖音', 'appPackage': 'com.ss.android.ugc.aweme', 'appActivity': 'com.ss.android.ugc.aweme.main.MainActivity'},
        {'appName': 'QQ音乐HD', 'appPackage': 'com.tencent.qqmusicpad','appActivity': 'ccom.tencent.qqmusicpad.activity.MainActivity'}]
    # 执行操作步骤
    operation_steps(2)



