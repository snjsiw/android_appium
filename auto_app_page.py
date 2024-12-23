import time

from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 定义通用的点击函数
def click_element(driver, locator, element_name=""):
    try:
        element = WebDriverWait(driver, 50).until(EC.visibility_of_element_located(locator))
        element.click()
        print(f"成功点击元素：{element_name} - {locator}")
        time.sleep(3)  # 等待1秒以确保操作完成
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"点击失败，未找到元素：{locator}，错误信息：{e}")

def send_element(driver, locator, key_words, element_name=""):
    try:
        element = WebDriverWait(driver, 50).until(EC.visibility_of_element_located(locator))
        element.send_keys(key_words)
        print(f"成功找到元素并输入内容：{element_name} - {locator}")
        time.sleep(3)  # 等待1秒以确保操作完成
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"输入失败，未找到元素：{locator}，错误信息：{e}")

def wait_element(driver, locator, element_name=""):
    try:
        element = WebDriverWait(driver, 50).until(EC.visibility_of_element_located(locator))
        print(f"成功找到元素：{element_name} - {locator}")
        time.sleep(3)  # 等待1秒以确保操作完成
        return element
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"未找到元素：{locator}，错误信息：{e}")