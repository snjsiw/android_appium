
import os
import subprocess
import random
import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from appium import webdriver
from auto_app_page import click_element

# 启动PCAPDroid会话
def start_pcapdroid_session(device_name):
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = '127.0.0.1:8011'
    # options.platform_version = '12'
    options.app_activity = 'com.emanuelef.remote_capture.activities.MainActivity'
    options.app_package = 'com.emanuelef.remote_capture'
    options.no_reset = True
    options.dont_stop_app_on_reset = True  # 防止重置和关闭应用
    # 初始化 WebDriver
    return webdriver.Remote(command_executor='http://127.0.0.1:4723/wd/hub', options=options)


# def start_pcapdroid_session(device_name):
#     options = UiAutomator2Options()
#     options.platform_name = 'Android'
#     options.device_name = 'emulator-5554'
#     options.platform_version = '9.0.57'
#     options.app_activity = 'com.emanuelef.remote_capture.activities.MainActivity'
#     options.app_package = 'com.emanuelef.remote_capture'
#     options.no_reset = True
#     options.dont_stop_app_on_reset = True  # 防止重置和关闭应用
#     # 初始化 WebDriver
#     return webdriver.Remote(command_executor='http://127.0.0.1:4723/wd/hub', options=options)


# 随机点击函数
def random_screen_click():
    screen_width = 720  # 替换为设备实际屏幕宽度
    screen_height = 1280  # 替换为设备实际屏幕高度
    x = random.randint(100, screen_width - 100)
    y = random.randint(100, screen_height - 100)
    adb_command = f"adb shell input tap {x} {y}"
    os.system(adb_command)
    print(f"已点击坐标: ({x}, {y})")

# 获取设备上所有已安装的应用包名
def get_installed_apps():
    result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], stdout=subprocess.PIPE)
    packages = result.stdout.decode('utf-8').splitlines()
    package_names = [pkg.split(":")[1] for pkg in packages]
    return package_names

# 获取应用的主Activity
def get_main_activity(package_name):
    result = subprocess.run(['adb', 'shell', 'cmd', 'package', 'resolve-activity', '--brief', package_name],
                            stdout=subprocess.PIPE)
    activity_info = result.stdout.decode('utf-8').strip()
    match = re.search(r'([a-zA-Z0-9\.]+)/([a-zA-Z0-9\./]+)', activity_info)
    return f"{match.group(1)}/{match.group(2)}" if match else None

# 获取PCAPDroid任务ID
def get_pcapdroid_task_id():
    result = subprocess.run(['adb', 'shell', 'dumpsys', 'activity', 'activities'], stdout=subprocess.PIPE)
    activities_info = result.stdout.decode('utf-8')
    for line in activities_info.splitlines():
        if 'com.emanuelef.remote_capture' in line and 'taskId' in line:
            match = re.search(r'taskId=(\d+)', line)
            return match.group(1) if match else None
    return None

# 切换回PCAPDroid应用，通过任务ID恢复
def switch_back_to_pcapdroid():
    task_id = get_pcapdroid_task_id()
    if task_id:
        os.system(f"adb shell am move-task-to-front {task_id}")
        print(f"已将PCAPDroid任务恢复到前台，任务ID: {task_id}")
    else:
        print("未找到PCAPDroid任务，无法恢复")

# 返回到主页
def return_to_home(driver):
    driver.press_keycode(3)  # 按下Home键
    print("返回到主页")

# 遍历所有应用并打开每个应用，跳过PCAPDroid和io.appium.settings，处理异常
def open_apps_and_random_clicks(driver, app_list, wait_time):
    count = 0  # 计数器，用于每打开4个应用后唤醒一次PCAPDroid
    for app in app_list:
        if app in ['com.emanuelef.remote_capture', 'io.appium.settings']:
            print(f"跳过应用：{app}")
            continue

        main_activity = get_main_activity(app)
        if main_activity:
            try:
                print(f"正在打开应用：{app}，主Activity：{main_activity}")

                # 强制停止应用
                os.system(f"adb shell am force-stop {app}")
                time.sleep(wait_time)  # 确保应用停止

                # 打开应用
                result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', main_activity],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(wait_time)  # 等待应用启动

                # 检查输出中的警告
                output = result.stderr.decode('utf-8')
                if "Warning: Activity not started" in output:
                    print(f"警告: 应用 {app} 已在运行，跳过该应用")
                    continue

                # 随机点击
                random_screen_click()

                # 退出应用进程
                os.system(f"adb shell am force-stop {app}")
                print(f"已强制停止应用：{app}")

                count += 1  # 计数器加1
                if count >= 4:  # 每打开4个应用唤醒一次PCAPDroid
                    switch_back_to_pcapdroid()
                    return_to_home(driver)
                    count = 0  # 重置计数器

            except Exception as e:
                print(f"无法打开应用 {app} 或在操作时出错，错误：{e}，跳过该应用")
                continue
        else:
            print(f"未找到主Activity：{app}")


# 执行步骤1和步骤2
def perform_step_1_and_2(driver, wait_time):
    time.sleep(wait_time)
    click_element(driver, (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="启动"]'), "启动按钮")
    time.sleep(wait_time)
    click_element(driver, (AppiumBy.XPATH, '//android.widget.TextView[@text="连接"]'), "查看连接")
    #click_element(driver, (AppiumBy.XPATH, '//android.widget.LinearLayout[@content-desc="连接"]'), "查看连接")
    time.sleep(wait_time)


# 执行步骤3和步骤4
def perform_step_3_and_4(driver, wait_time):
    time.sleep(wait_time)
    click_element(driver, (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="保存到文件"]'), "点击保存到文件")
    time.sleep(wait_time)
    click_element(driver, (AppiumBy.XPATH, '//android.widget.Button[@resource-id="android:id/button1"]'), "点击保存")
    time.sleep(wait_time)

    # # 第十二步：保存PCAP到本地
    # print(new_file_name)
    # os.system(f"adb pull /sdcard/{new_file_name} C:/Users/lenovo/Desktop/android_appium/TEST")
    # time.sleep(5)  # 等待应用停止


# 主逻辑执行
if __name__ == "__main__":
    # 填写设备名称
    devices_name = '127.0.0.1:8011'
    driver = start_pcapdroid_session(devices_name)
    try:
        # 执行步骤1和步骤2
        perform_step_1_and_2(driver, 1)

        # 返回主页
        return_to_home(driver)
        # 获取所有已安装应用的包名
        installed_apps = get_installed_apps()
        # 打开其他应用并执行随机点击
        open_apps_and_random_clicks(driver, installed_apps, 2)
        # 切换回PCAPDroid应用
        subprocess.run(['adb', '-s', devices_name, 'shell', 'am', 'start', '-n',
                        'com.emanuelef.remote_capture/com.emanuelef.remote_capture.activities.MainActivity'])
        # 执行步骤3和步骤4
        perform_step_3_and_4(driver, 1)
    finally:
        # 退出会话
        driver.quit()
