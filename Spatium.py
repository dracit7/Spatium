import requests
import struct
import re
import json
import ssl
import time
import sys
import os
import threading
import urllib.request
import tkinter
import tkinter.font
import tkinter.messagebox
from PIL import Image,ImageTk


def BuildHeader(RefererUrl,TargetUrl):
  '''
  Build a fake header to get the video from website.
  '''
  Addr = re.search('//.*?/',TargetUrl)
  beg , end = Addr.span()
  Host = TargetUrl[beg+2:end-1]
  Header = [
    ('Host', Host),
    ('Connection', 'keep-alive'),
    ('Origin', 'https://www.bilibili.com'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'),
    ('Accept', '*/*'),
    ('Referer', RefererUrl),
    ('Accept-Language', 'zh-CN,zh;q=0.9'),
    ('Accept-Encoding', 'gzip, deflate, br'),
  ]
  return Header

def report(count, blockSize, totalSize):
  '''
  Reporthook function.
  Report progress information in form of a processbar.
  '''
  downloadedSize = count * blockSize
  percent = downloadedSize * 100 / totalSize
  Progress.set(f"{int(percent)} %")
  ProgressBar.coords(Bar,(2,2,6*percent,19))
  BaseWindow.update()

def SetCookies(RawCookie):
  '''
  Make fake cookies to get videos which have best quality.
  '''
  RawCookie.set("buvid3","B1B3A2FE-A9F9-4DE7-9799-5C805F7D44EE27891infoc")
  # You can change the UserID and ckMd5 into your account. That would be more convenient.
  RawCookie.set("DedeUserID","357146416")
  RawCookie.set("DedeUserID__ckMd5","6e61880a0cda1994")
  RawCookie.set("CURRENT_QUALITY","80") # Don't think you can get the video only with this.
  return RawCookie

class VideoDownloader(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):

    ssl._create_default_https_context = ssl._create_unverified_context

    # Get target url from GUI
    RefererUrl = InputBox.get()
    InputBox.delete(0,tkinter.END)

    # Get cookies from website and change it
    try:
      ResponseFromWeb = requests.get(RefererUrl)
    except:
      Output.set('目前本抓取器只支持Bilibili的普通视频下载,请检查您的url是否正确(番剧下载请出门右拐Dilidili,滑稽)')
      return
    RawCookie = ResponseFromWeb.cookies
    Cookie = SetCookies(RawCookie)

    # Get the source code of the video page
    Output.set('正在向次元墙的另一边请求传送视频,请稍等~')
    ResponseFromWeb = requests.get(RefererUrl,cookies=RawCookie)
    RawPost = ResponseFromWeb.text

    # Get Name
    Addr = re.search(r'"title":".*?"',RawPost)
    try:
      beg , end = Addr.span()
    except:
      Output.set('等等...这个报文！这不是来自Bilibili的报文吧！别搞错了哦。')
      return
    VideoName = RawPost[beg+9:end-1]
    try:
      if not os.path.exists(UserConfig['SavePath']):
        os.makedirs(UserConfig['SavePath'])
      if not os.path.exists(UserConfig['SavePath']+"\\"+VideoName):
        os.mkdir(UserConfig['SavePath']+"\\"+VideoName)
    except:
      if not os.path.exists(UserConfig['SavePath']):
        os.makedirs(UserConfig['SavePath'])
      if not os.path.exists(UserConfig['SavePath']+"\\这个视频名无法解析"):
        os.mkdir(UserConfig['SavePath']+"\\这个视频名无法解析")
      VideoName = '这个视频名无法解析'

    # Decipher
    Addr = re.search(r'"durl":\[.*\}\],"seek',RawPost)
    try:
      beg , end = Addr.span()
    except:
      Output.set('这个报文...无法解析！您输入的真的是Bilibili视频的地址吗?')
      return
    Post = RawPost[beg+8:end-7]
    print(Post)
    
    FileInfo=[]
    FileDicts=[]

    Addr=re.search(r'\},\{',Post)
    while Addr != None:
      beg , end = Addr.span()
      FileInfo.append(Post[:beg+1])
      Post=Post[end-1:]
      Addr=re.search(r'\},\{',Post)
    FileInfo.append(Post)

    for i in range(0,len(FileInfo)):
      FileDicts.append(json.loads(FileInfo[i]))

    # Print file information
    FileNum = len(FileDicts)
    Output.set("视频信息获取完毕,共有"+str(FileNum)+"个文件")
    time.sleep(2)

    # Recieve videos
    for i in range(0,FileNum):
      Header = BuildHeader(RefererUrl,FileDicts[i]['url'])
      opener = urllib.request.build_opener()
      opener.addheaders = Header
      urllib.request.install_opener(opener)
      FileName = UserConfig['SavePath']+'\\'+VideoName+"\\Part{}.flv".format(i+1)
      Output.set("开始传送文件{},还剩{}个".format(i+1,FileNum-i-1))
      try:
        urllib.request.urlretrieve(FileDicts[i]['url'],filename=FileName,reporthook=report)
      except:
        Output.set("文件传送中出了一点小问题......请检查一下您的网络连接是否正常,然后重新下载。")
        ProgressBar.coords(Bar,(2,2,2,19))
        Progress.set(f'下载失败')
        BaseWindow.update()
        return
    Output.set('所有文件传送完毕.')

    if UserConfig['IfConnect'] == 1:
      import moviepy.editor
      Output.set("正在拼接视频 ... (由于python的效率问题这可能会比较漫长,请耐心等待)")
      VideoPart = []
      for i in range(0,FileNum):
        VideoPart.append(moviepy.editor.VideoFileClip(UserConfig['SavePath']+'\\'+VideoName+"\\Part{}.flv".format(i+1)))
      Video = moviepy.editor.concatenate_videoclips(VideoPart)
      Video.write_videofile(UserConfig['SavePath']+'\\'+VideoName+'.mp4')
      Output.set("拼接完成.")

def DownloadVideo():
  Downloader = VideoDownloader()
  Downloader.start()

def GetHelp():
  pass


# The Body of the Program
# Main function

# Read Configs
try:
  with open('UserConfig.txt','r') as file:
    UserConfig = json.load(file)
except:
  tkinter.messagebox.showinfo(message="用户信息文件UserConfig.txt丢失,请运行Config程序来更新设置。")
  os.sys.exit()

# Build the window
BaseWindow = tkinter.Tk()
BaseWindow.title('Spatium')
BaseWindow.resizable(0,0)

# Add Background
try:
  BackgroundImage = Image.open(r'Images\\Background.gif')
except:
  tkinter.messagebox.showinfo(message='背景载入失败,您是不是乱动Images文件夹了?哼......')
  os.sys.exit()
Background = ImageTk.PhotoImage(BackgroundImage)
Width,Height = Background.width(),Background.height()
BaseWindow.geometry('{}x{}'.format(Width,Height))
Background_Label = tkinter.Label(BaseWindow,image=Background)
Background_Label.place(x=0,y=0,relwidth=1,relheight=1)

# Set fonts
font = tkinter.font.Font(family='MPlantin',size=19)

# Add Output bar
Output = tkinter.StringVar()
Output_Label = tkinter.Label(BaseWindow,bg='Lavender',fg='Black',textvariable=Output,width=100)
Output_Label.place(x=180,y=200)
Output.set('输出信息会显示在这里,有什么问题看这里就Ok啦')

# Build start button
try:
  ButtonImage = Image.open(r'Images\\MainButton.gif')
except:
  tkinter.messagebox.showinfo(message='按钮图片找不到了,都说了不要动Images文件夹啦...')
  os.sys.exit()
ButtonImage = ImageTk.PhotoImage(ButtonImage)
Button = tkinter.Button(BaseWindow,image=ButtonImage,borderwidth=0,command=DownloadVideo)
Button.place(x=320,y=310)

# Add inputbox
InputBox = tkinter.Entry(BaseWindow,width=62,borderwidth=0,font=font,background='Lavender')
InputBox.place(anchor='nw',x=40,y=100)

# Add progress bar
Progress = tkinter.StringVar()
ProgressBar = tkinter.Canvas(BaseWindow,width=600,height=18,borderwidth=0)
ProgressBar.place(x=235,y=230)
ProgressBar.create_rectangle(2,2,600,19,outline='SkyBlue')
Bar = ProgressBar.create_rectangle(2,2,2,19,outline='',width=0,fill='SkyBlue')
Text = ProgressBar.create_text(300,10,text=Progress.get(),fill='Navy')

def Update(varname, index, mode):
  ProgressBar.itemconfigure(Text,text=BaseWindow.getvar(varname))
Progress.trace_variable('w',Update)

Help = tkinter.Menu(BaseWindow)
Help.add_command(label='这里(暂时)是Bilibili专用视频抓取器Spatium')
Help.add_command(label='      ')
Help.add_command(label='请保持目录内的Images文件夹和Userconfig.txt文件完好无损哦')
Help.add_command(label='      ')
Help.add_command(label='视频默认保存在Videos文件夹里哦')
BaseWindow.config(menu=Help)

BaseWindow.mainloop()

