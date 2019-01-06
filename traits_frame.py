#-*- coding: utf-8 -*-

import wx
import os
import json
import traceback
import logging

#异常处理
logging.basicConfig(filename = "log.txt", level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


from chrome_toutiao_auto import chrome_toutiao_auto, COOKIE_FILE_NAME
from chrome_toutiao_auto import NoDriverException, NoSuchTabException, RetryTimesException

#配置文件保存文件名
CONFIG_FILE_NAME = "config.txt"

class MainFrame(wx.Frame):

	def __init__(self):
		wx.Frame.__init__(self, None, -1, 'chrome toutiao auto', size = (500, 250), style = wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX)

		main_sizer = wx.BoxSizer(wx.VERTICAL)

		#第一行
		loop_sizer = wx.BoxSizer(wx.HORIZONTAL)

		#第二行
		tab_name_sizer = wx.BoxSizer(wx.HORIZONTAL)

		#第三行
		func_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		#第四行
		start_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		main_sizer.Add(loop_sizer, 0, wx.EXPAND | wx.ALL, 5)
		main_sizer.Add(tab_name_sizer, 0, wx.EXPAND | wx.ALL, 5)
		main_sizer.Add(func_btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
		main_sizer.Add(start_btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

		#第一行：循环次数，是否从新下标开始
		loop_static_text = wx.StaticText(self, wx.ID_ANY, u"循环次数")
		self.loop_times_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (80, 30), 0)

		new_id_static_text = wx.StaticText(self, wx.ID_ANY, u"是否从新的下标开始")
		new_id_static_text.SetToolTip(u"头条广告方案不能重名，如果提示重名，勾选此选项重新执行")

		self.new_id_checkbox = wx.CheckBox(self, wx.ID_ANY, '')

		loop_sizer.Add(loop_static_text, 0, wx.EXPAND | wx.ALL, 5)
		loop_sizer.Add(self.loop_times_ctrl, 0, wx.EXPAND | wx.ALL, 5)
		loop_sizer.Add(new_id_static_text, 0, wx.EXPAND | wx.ALL, 5)
		loop_sizer.Add(self.new_id_checkbox, 0, wx.EXPAND | wx.ALL, 5)

		#第二行：侧边栏名字
		tab_static_text = wx.StaticText(self, wx.ID_ANY, u"广告组名称")
		self.tab_name_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (400, 30), 0)

		tab_name_sizer.Add(tab_static_text, 0, wx.EXPAND | wx.ALL, 5)
		tab_name_sizer.Add(self.tab_name_ctrl, 0, wx.EXPAND | wx.ALL, 5)

		#第三行：清除cookie按钮，保存cookie
		self._save_cookie_btn_id = wx.NewId()
		self.save_cookie_btn = wx.Button(self, self._save_cookie_btn_id, u"保存账号", wx.DefaultPosition, (80, 40), 0)
		self.save_cookie_btn.SetToolTip(u"首次使用需要手动登录账号，然后点击此按钮将账号信息保存。\n注意：切勿将文件夹下的cookie.txt泄露，否则您的账号密码将会泄露。")
	
		self._clear_cookie_btn_id = wx.NewId()
		self.clear_cookie_btn = wx.Button(self, self._clear_cookie_btn_id, u"清除账号", wx.DefaultPosition, (80, 40), 0)
		self.clear_cookie_btn.SetToolTip(u"如需更换账号，请点击此按钮清理")
		
		func_btn_sizer.Add(self.save_cookie_btn, 0, wx.EXPAND | wx.ALL, 5)
		func_btn_sizer.Add(self.clear_cookie_btn, 0, wx.EXPAND | wx.ALL, 5)

		#第四行：开始循环执行
		self._start_btn_id = wx.NewId()
		self.start_process_btn = wx.Button(self, self._start_btn_id, u"开始", wx.DefaultPosition, (80, 40), 0)
		self.start_process_btn.SetToolTip(u"填写完上面的信息后点击此按钮执行。上述配置将会自动保存，下次不需重新输入")

		start_btn_sizer.Add(self.start_process_btn, 0, wx.EXPAND | wx.ALL, 5)

		self.SetSizer(main_sizer)

		#加载上次使用时的配置
		self.load_default_config()

		self.chrome_toutiao_auto = chrome_toutiao_auto()

		self.init_event()

	def init_event(self):
		self.Bind(wx.EVT_BUTTON, self.on_btn_save_cookie, id = self._save_cookie_btn_id)
		self.Bind(wx.EVT_BUTTON, self.on_btn_clear_cookie, id = self._clear_cookie_btn_id)
		self.Bind(wx.EVT_BUTTON, self.on_btn_start_process, id = self._start_btn_id)

	def on_btn_save_cookie(self, event):
		self.chrome_toutiao_auto.dumpCookies()

	def on_btn_clear_cookie(self, event):
		dialog = wx.MessageDialog(self, u'是否真的要清除账号信息？', u'账号清除', 
								wx.YES_NO | wx.ICON_QUESTION)

		if dialog.ShowModal() == wx.ID_YES:
			if (os.path.exists(COOKIE_FILE_NAME) and os.path.isfile(COOKIE_FILE_NAME)):
				os.remove(COOKIE_FILE_NAME)

		wx.MessageBox(u"清除完毕！", u"提示", wx.OK)

	def on_btn_start_process(self, event):
		#开始时先保存当前的配置
		self.save_default_config()

		loop_times = self.loop_times_ctrl.GetValue()
		is_new_id = self.new_id_checkbox.IsChecked()
		tab_name = self.tab_name_ctrl.GetValue()

		try:
			#开始执行
			self.chrome_toutiao_auto.operationAuth(times, is_new_id, tab_name)
		except NoDriverException as e:
			self.chrome_toutiao_auto.showNoDriverMessage()

			s = traceback.format_exc()
			logging.error(s)
		except NoSuchTabException as e:
			wx.MessageBox(u"找不到对应广告组，请检查拼写是否错误", "error", wx.OK)

			s = traceback.format_exc()
			logging.error(s)
		except RetryTimesException as e:
			s = traceback.format_exc()
			logging.error(s)
		except Exception as e:
			wx.MessageBox(u"程序发生未知异常，请关闭程序和浏览器重试。请将文件夹下的log.txt发送给维护程序检查问题", "error", wx.OK)

			s = traceback.format_exc()
			logging.error(s)

	def save_default_config(self):
		loop_times = self.loop_times_ctrl.GetValue()
		is_new_id = self.new_id_checkbox.IsChecked()
		tab_name = self.tab_name_ctrl.GetValue()

		config = {'loop_times' : loop_times, 'is_new_id' : is_new_id, 'tab_name' : tab_name}

		with open(CONFIG_FILE_NAME, 'w') as f:
			f.write(json.dumps(config))

	def load_default_config(self):
		if (os.path.exists(CONFIG_FILE_NAME) and os.path.isfile(CONFIG_FILE_NAME)):
			with open(CONFIG_FILE_NAME, 'r') as f:
				config = f.read()

				if config is not None and config != "":
					config = json.loads(config)
					loop_times = config[u"loop_times"]
					is_new_id = config[u"is_new_id"]
					tab_name = config[u"tab_name"]

					loop_times and self.loop_times_ctrl.SetValue(loop_times)
					is_new_id and self.new_id_checkbox.SetValue(is_new_id)
					tab_name and self.tab_name_ctrl.SetValue(tab_name)
