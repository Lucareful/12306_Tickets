# -*- coding: utf-8 -*-
import json
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
# 判断YDMHTTP模块是否在python环境中（我的是不在，所以加上去）
import sys

sys.path.insert(1, r"YDMHTTP.py")
from YDMHTTP import decode

browser = webdriver.Chrome()
browser.maximize_window()

linktypeid = "dc"
fs = "北京"
ts = "武汉"
date = "2020-01-13"
flag = "N,N,Y"

base_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid={}&fs={},BJP&ts={},WHN&date={}&flag={}'
url = base_url.format(linktypeid, fs, ts, date, flag)

browser.get(url)

wait = WebDriverWait(browser, 10, 0.5)

# 通过时间判定选择预定车次
# 寻找tr标签中的 属性id 已 ’ticket_‘ 开头的数据
tr_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//tr[starts-with(@id, "ticket_")]')))

for tr in tr_list:
    date_string = tr.find_element_by_class_name("start-t").text
    # 判断时间是否在符合你想要的时间范围中
    tr.find_element_by_class_name('no-br').click()
    # print(date_string)
    break

# 点击账号 异步加载需要显性等待
wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "账号登录"))).click()
# browser.find_element_by_link_text("账号登录").click()

# 输入用户名和密码（我将我的用户名和密码保存在了json文件中，若别人使用需要更改）
with open("account.json", "r", encoding="utf-8") as f:
    account = json.load(f)

browser.find_element_by_id("J-userName").send_keys(account["username"])
browser.find_element_by_id("J-password").send_keys(account["password"])

# 获取全屏截图
full_img_data = browser.get_screenshot_as_png()

# 截取验证图片
login_img_element = wait.until((EC.visibility_of_element_located((By.ID, "J-loginImg"))))

# 计算截图位置
# 截取验证码的位置
scale = 2.0
x1 = login_img_element.location["x"]
y1 = login_img_element.location["y"]
x2 = x1 + login_img_element.size["width"] * scale
y2 = y1 + login_img_element.size["height"] * scale

cut_info = (x1, y1, x2, y2)

# 把全屏图片构建成全屏图片操作对象
full_img = Image.open(BytesIO(full_img_data))

# 通过截图信息对象截取图片
cut_img = full_img.crop(cut_info)

# 把图片保存到本地
cut_img.save('demo.png')

# 将验证图片发送到打码平台
result = decode('demo.png', codetype=6701)

# 定义八个点击坐标点
positions = [
    (7.30*25, 140),
    (10.58*25, 140),
    (13.83*25, 140),
    (17.11*25, 140),
    (7.30*25, 250),
    (10.58*25, 250),
    (13.83*25, 250),
    (17.05*25, 250)
]

# 模拟点击坐标
for num in result:
    position = positions[int(num) - 1]
    # 动作对象
    ActionChains(browser).move_to_element_with_offset(login_img_element, position[0]/2, position[1]/2).click().perform()

# 点击登录
browser.find_element_by_id("J-login").click()

# 点击选择乘车人
wait.until(EC.visibility_of_element_located((By.ID, "normalPassenger_0")))

# 点击提交订单
browser.find_element_by_id("submitOrder_id").click()

time.sleep(5)
