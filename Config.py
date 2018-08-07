import json
import time
import sys
import os
import threading
import tkinter
import tkinter.font
from PIL import Image,ImageTk

def SaveConfig():
	if not SavePath.get() == '':
		UserConfig['SavePath'] = SavePath.get()
	with open('UserConfig.txt','w+') as file:
		json.dump(UserConfig,file)
	os.sys.exit()

def ChangeVar():
  UserConfig['IfConnect'] = IfConnect.get()

def Quit():
	os.sys.exit()

OptionsWindow = tkinter.Tk()
OptionsWindow.title('Options')
OptionsWindow.geometry('460x150')

with open('UserConfig.txt','r') as file:
  UserConfig = json.load(file)

IfConnect = tkinter.IntVar()
IfConnect.set(UserConfig['IfConnect'])

ConnectButton = tkinter.Checkbutton(OptionsWindow,text='在文件下载完成后自动拼接(不推荐，速度较慢，建议使用格式工厂)',variable=IfConnect,command=ChangeVar)
ConnectButton.place(x=40,y=70)

SavePath_Label = tkinter.Label(OptionsWindow,text='请输入下载文件所在文件夹的路径：')
SavePath_Label.place(x=40,y=10)
SavePath = tkinter.Entry(OptionsWindow,width=50)
SavePath.place(x=40,y=40)

SaveButton = tkinter.Button(OptionsWindow,text='保存设置',command=SaveConfig)
CancelButton = tkinter.Button(OptionsWindow,text='取消',command=Quit)
SaveButton.place(x=300,y=110)
CancelButton.place(x=400,y=110)

OptionsWindow.mainloop()