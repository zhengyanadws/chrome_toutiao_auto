# -*- coding: utf-8 -*- 

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import wx
import json
import time
import re
import os
import traceback

#cookie保存文件名
COOKIE_FILE_NAME = "cookie.txt"

#头条URL
URL = "https://ad.toutiao.com/overture/data/advertiser/ad/"

#找不到浏览器对象
class NoDriverException(Exception):
	def __init__(self):
		super(NoDriverException, self).__init__()

#找不到对应tab
class NoSuchTabException(Exception):
	def __init__(self):
		super(NoSuchTabException, self).__init__()	

#超时次数过多
class RetryTimesException(Exception):
	def __init__(self):
		super(RetryTimesException, self).__init__()	

class chrome_toutiao_auto(object):
	def __init__(self):
		self.driver = None

		try:
		#开启浏览器
			self.driver = self.openChrome()
			#读取cookie
			self.readCookies()
			#加载页面
			self.openUrl()
		except Exception as e:
			traceback.print_exc()
			self.showNoDriverMessage()

	def showNoDriverMessage(self):
		wx.MessageBox(u"浏览器创建失败，\
				请检查文件夹下的chromedriver.exe版本是否与您当前chrome版本号一致，\
				版本号对应请查阅readme.txt文档", "error", wx.OK)

	def showTimeoutMessage(self):
		wx.MessageBox(u"查找元素超时，请检查网络并重启浏览器和程序重试一次，\
			同时请检查最后一次复制的方案内容是否正常", "error", wx.OK)

	def checkDriver(self):
		if self.driver is None:
			self.showNoDriverMessage()

		raise NoDriverException()

	def openChrome(self):
		# 加启动配置
		option = webdriver.ChromeOptions()
		option.add_argument('disable-infobars')

		# 打开chrome浏览器
		driver = browser = webdriver.Chrome(executable_path ="chromedriver")
		return driver

	def waitSomeTimeByXpath(self, xpath, retry_times = 3):
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, xpath))
			)
		except TimeoutException as e:
			if retry_times == 0:
				self.showTimeoutMessage()
				raise RetryTimesException()

			self.driver.refresh()
			self.waitSomeTimeByXpath(xpath, retry_times - 1)

	def waitSomeTimeByClassName(self, className, retry_times = 3):
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME , className))
			)
		except TimeoutException as e:
			if retry_times == 0:
				self.showTimeoutMessage()
				raise RetryTimesException()

			self.driver.refresh()
			self.waitSomeTimeByXpath(xpath, retry_times - 1)

	def dumpCookies(self):
		cookies = self.driver.get_cookies()

		with open(COOKIE_FILE_NAME, 'w') as f:
			f.write(json.dumps(cookies))

	def readCookies(self):
		f = None
		cookie = []

		if (os.path.exists(COOKIE_FILE_NAME) and os.path.isfile(COOKIE_FILE_NAME)):
			with open(COOKIE_FILE_NAME, 'r') as f:
				cookie = f.read()
				cookie = json.loads(cookie)

		for c in cookie:
			self.add_cookie(c)

	def openUrl(self):
		self.driver.get(URL)	

	# 授权操作
	def operationAuth(self, times, is_new_id, tab_name):
		#检查参数是否合法
		if times <= 0 or tab_name is None:
			return

		if tab_name != "":
			find_tab = False

			self.waitSomeTimeByClassName(self.driver, "title-block")

			title_block_list = self.driver.find_elements_by_class_name("title-block")
			for title_block in title_block_list:
				tab_links = title_block.find_elements_by_tag_name("a")
				tab_link = tab_links[0]

				if tab_link.get_attribute("title") == tab_name:
					find_tab = True
					tab_link.click()
					break

			if find_tab == False:
				raise NoSuchTabException()

			time.sleep(2)

		for time in xrange(1, times):
			self.waitSomeTimeByClassName(self.driver, "operation-cell")

			oper_elems = self.driver.find_elements_by_class_name("operation-cell")

			links = oper_elems[0].find_elements_by_tag_name("a")
			links[1].click()
		 
			time.sleep(1)
			btn_success = self.driver.find_element_by_xpath('//*[@id="pagelet-promotion-details"]/div[2]/div/div[7]/div[2]/div/div/div[3]/div/div/div[1]')
			btn_success.click()

			self.waitSomeTimeByXpath(self.driver, '/html/body/div[1]/div[2]/div/div[3]/div[6]/div/div[2]/div[3]/div/input')

			plan_name_ctrl = self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[3]/div[6]/div/div[2]/div[3]/div/input")
			plan_name = plan_name_ctrl.get_attribute("value")
			new_plan_name = plan_name

			#如果从新的id开始，则直接拼一个_1，否则去分析当前第一个元素的编号，累加
			if is_new_id == True:
				new_plan_name = new_plan_name + "_" + 1
			else:
				plan_name_args = plan_name.split("_")
				idx = len(plan_name_args) > 1 and int(plan_name_args[1]) or 0
				idx += 1
				new_plan_name = plan_name_args[0] + "_" + str(idx)

			plan_name_ctrl.clear()
			plan_name_ctrl.send_keys(new_plan_name)

			self.waitSomeTimeByXpath(self.driver, '/html/body/div[1]/div[2]/div/div[3]/div[7]/div/div[2]/button[3]')

			save_and_create_new_btn = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[3]/div[7]/div/div[2]/button[3]')
			save_and_create_new_btn.click()

			self.waitSomeTimeByXpath(self.driver, '//*[@id="pagelet-create-creative-app"]/div/div/div/div[1]/div[8]/div/div/div/div/div[2]')

			submit_btn = self.driver.find_element_by_xpath('//*[@id="pagelet-create-creative-app"]/div/div/div/div[1]/div[8]/div/div/div/div/div[2]')
			submit_btn.click()

			self.waitSomeTimeByXpath(self.driver, '//*[@id="table-section"]/table/tbody/tr[1]/td[2]/div/label/div')

			cancel_btn = self.driver.find_element_by_xpath('//*[@id="table-section"]/table/tbody/tr[1]/td[2]/div/label/div')
			cancel_btn.click()

			is_new_id = False