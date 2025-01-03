import json
import threading
import time
import socket
import tkinter as tk
from tkinter import filedialog, scrolledtext

import requests

Host = '0.0.0.0'
Port = 18110
APIKey = ""
SecretKey = ""
access_token = ""
aiContent = ("#你是一个病毒样本总结者，我会发给你一个病毒文件扫描结果。"
             "首先会是一个用户名（username）+ ==>，后面分成两个部分，FilePath和FileInformation。"
             "FilePath中包含路径和病毒的特征类型，Information包含病毒文件的所有内容。" 
             "如果Information中内容是This file cannot read, which is maybe as a zip file or others."
             "则说明该文件不是文本文件，但是依然是病毒文件。"
             "你需要回复的格式：\n"
             "=========<username1>=========+\n病毒报告：<关于第一个用户的病毒报告和推荐防御机制>\n\n"
             "=========<username2>=========+\n病毒报告：<关于第二个用户的病毒报告和推荐防御机制>\n\n"
             "<以此输出所有的用户报告>......")


def warningMethod():
    print("执行警报程序")


class MainApp:
    def __init__(self, root):
        self.activate = True
        self.aiTk = None
        self.aiInformation = ""
        self.aiMSG = ""
        self.root = root
        self.root.title("User Manager")
        self.column_count = 0  # 初始化列数
        self.root.iconbitmap("Theme.ico")
        # 创建顶部面板
        self.top_panel = tk.Frame(self.root, bg='lightblue', padx=10, pady=10)
        self.top_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        # 创建滑块
        self.scale = tk.Scale(self.top_panel, from_=10, to=600, orient=tk.HORIZONTAL)
        self.scale.pack(fill=tk.BOTH, pady=5)
        # 创建文本框
        self.text_box = tk.Entry(self.top_panel, width=20)  # 设置文本框宽度为20
        self.text_box.pack(side=tk.LEFT, fill=tk.X, expand=True)  # 让文本框填充剩余空间
        # 创建“Config”按钮
        self.config_button = tk.Button(self.top_panel, text="AI助手", command=self.aiPanel)
        self.config_button.pack(side=tk.LEFT, fill=tk.X, padx=5)  # 按钮也在同一行，但宽度固定
        # 创建底部面板
        self.bottom_panel = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.bottom_panel.pack(fill=tk.BOTH, expand=True, pady=5)

    def addPanel(self):
        # 每次添加面板时，列数加1
        self.column_count += 1
        sub_panel = tk.Frame(self.bottom_panel, bd=1, relief=tk.SUNKEN)
        sub_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        return sub_panel

    def aiPanel(self):
        aimsg = "ChatGPT will tell you something."
        if self.aiTk is None or not self.aiTk.winfo_exists():
            self.aiTk = tk.Toplevel(self.root)
            self.aiTk.geometry("400x500")
            self.aiTk.title("AI Panel")
            self.aiTk.resizable(False, False)
            text_area = scrolledtext.ScrolledText(self.aiTk, wrap=tk.WORD, width=400, height=500)
            text_area.pack(pady=50)
            text_area.insert(tk.END, self.aiMSG)
            text_area.config(state=tk.DISABLED)
            text_area.yview_moveto(0)

    def config_action(self):
        # 获取滑块的值和文本框的内容
        scale_value = self.scale.get()
        text_value = self.text_box.get()
        # 拼接成一个字符串
        result = f"{scale_value} {text_value}"
        return result

    def rearrange_widgets(self):
        # 重新排列所有widget，使它们填充整个水平空间
        for widget in self.bottom_panel.winfo_children():
            widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)


class SocketBody:
    def __init__(self,conn):
        self.headLength = 10
        self.conn = conn
        print("There was an user connected the service.")
        self.recvData = bytes()
        self.obj = UserObj(self)
        self.thread = threading.Thread(target=self.receiveMSG)
        self.thread.start()
        self.timeTest()

    def sendMSG(self, msg: str):
        # print(msg)
        if not isinstance(msg, str):
            body = msg
            headPack = "0" * (10 - len(str(len(body)))) + str(len(body))
            self.conn.send(headPack.encode())
            self.conn.send(body)
            return
        else:
            body = msg.encode()
        headPack = "0" * (10 - len(str(len(body)))) + str(len(body))
        sendData = headPack.encode() + body
        try:
            self.conn.send(sendData)
        except Exception as e:
            print("sendMSG:", e)

    def receiveMSG(self: socket):
        try:
            while app.activate:
                    # print(1)
                    while len(self.recvData) < self.headLength:
                        # print(2)
                        self.recvData += self.conn.recv(1024)
                    headPack = self.recvData[:self.headLength]
                    bodyLength = int(headPack.decode())
                    body = self.recvData[self.headLength:]
                    while len(body) < bodyLength:
                        # print(3)
                        body += self.conn.recv(1024)
                    self.recvData = body[bodyLength:]
                    body = body[:bodyLength]
                    self.manipulate(body)
        except Exception as e:
            self.__del__()
            print("receiveMSG:", e)

    def manipulate(self, body):
        body = body.decode()
        body = body.split("|")
        # print(body)
        if body[0] == " ":
            self.time = (time.time_ns() - self.time)//1000000
            if self.time > 1000:
                self.time = 999
            self.obj.label.config(text=str(self.time) + "ms")
        if body[0] == "name":
            self.name = body[1]
            self.obj.name.config(text=self.name)
        if body[0] == "Warning":
            warningMethod()
            for widget in self.obj.top_panel.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(bg="red")
            if len(access_token) > 0:
                app.aiInformation += self.name + "==>\n" + body[1]
                app.aiMSG = getMSG(app.aiInformation)
        if body[0] == "database":
            self.obj.addText(body[1].split(" "))
        if body[0] == "shutdown":
            self.obj.childPanel.destroy()
            self.__del__()

    def timeTest(self, event = None):
        self.sendMSG(" " +"|")
        self.time = time.time_ns()

    def __del__(self):
        self.conn.close()
        self.obj.childPanel.destroy()
        app.rearrange_widgets()




class UserObj:
    def __init__(self, sockBody):
        self.socket = sockBody
        self.childPanel = app.addPanel()
        self.create_main_panel()

    def on_text_click(self, event):
        # 获取文本组件
        text = event.widget
        name = text.cget("text")
        # 将文本变为灰色
        text.config(bg='gray')
        # 1秒后恢复原色
        text.after(500, lambda: text.config(bg='white'))
        # 执行单击操作
        print(f"{name} 被单击")

    def on_text_double_click(self, event):
        # 获取文本组件
        text = event.widget
        self.socket.sendMSG("del|"+text.cget("text"))
        text.destroy()


    def on_button_click(self, button_name):
        # 按钮点击事件处理函数
        if button_name == "配置":
            self.socket.sendMSG("config|"+app.config_action())
            print("配置按钮被点击")
        if button_name == "加载":
            self.socket.sendMSG("load|")
            print("加载按钮被点击")
        if button_name == "查杀":
            self.socket.sendMSG("scan" + "|")
        if button_name == "更新库":
            file_path = filedialog.askopenfilename()
            if file_path:
                print(f"选择的文件地址是：{file_path}")
                self.socket.sendMSG("database|"+file_path.split("/")[-1])
                self.socket.sendMSG(get_file(file_path))
                self.socket.sendMSG("content|")
            else:
                print("没有选择文件")

    def addText(self, texts):
        for x in self.bottom_panel.winfo_children():
            x.destroy()
        for text in texts:
            text_widget = tk.Label(self.bottom_panel, text=text, bg='white', fg='black')
            text_widget.pack(fill='x')
            # 绑定单击事件
            text_widget.bind("<Button-1>", self.on_text_click)
            # 绑定双击事件
            text_widget.bind("<Double-1>", self.on_text_double_click)

    def create_main_panel(self):
        # 创建上方面板，横向排列两个按钮
        top_panel = tk.Frame(self.childPanel)
        top_panel.pack(fill='x')
        self.name = tk.Label(top_panel, text="----")
        self.name.pack(side='left')
        self.label = tk.Label(top_panel, text="--ms")
        self.label.bind("<Button-1>", self.socket.timeTest)
        self.label.pack(side='left')
        config_button = tk.Button(top_panel, text="配置", command=lambda: self.on_button_click("配置"))
        config_button.pack(side='left')
        config_button = tk.Button(top_panel, text="加载", command=lambda: self.on_button_click("加载"))
        config_button.pack(side='left')
        update_button = tk.Button(top_panel, text="更新库", command=lambda: self.on_button_click("更新库"))
        update_button.pack(side='left')
        config_button = tk.Button(top_panel, text="查杀", command=lambda: self.on_button_click("查杀"))
        config_button.pack(side='left')
        # 创建下方面板
        self.top_panel = top_panel
        self.bottom_panel = tk.Frame(self.childPanel)
        self.bottom_panel.pack(fill='both', expand=True)

def SocketManager():
    server_socket.listen(5)
    while app.activate:
        client_socket, client_address = server_socket.accept()
        SocketBody(client_socket)

def get_file(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
        return content

def getAcceesstoken():
    url = f"https://aip.baidubce.com/oauth/2.0/token?client_id={APIKey}&client_secret={SecretKey}&grant_type=client_credentials"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")  if response.json().get("access_token") is not None else ""

def getMSG(fileInformation):
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token={access_token}"
    payload = json.dumps({
        "system": aiContent,
        "messages": [
            {
                "role": "user",
                "content": fileInformation
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    return data.get('result', '')

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    root.resizable(True, False)
    access_token = getAcceesstoken()
    app = MainApp(root)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((Host, Port))
    thread = threading.Thread(target=SocketManager)
    thread.start()
    root.mainloop()
    app.activate = False

