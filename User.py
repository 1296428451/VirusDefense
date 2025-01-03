import os
import sys
import threading
import time
import socket
import subprocess
import tkinter as tk

Host = '127.0.0.1'
Port = 18110
Interval = 60
Path = "C:\\Users\\ASUS\\Desktop\\clamav\\"
UserName = "PC1"
CheckPath = "F:\\UserFiles\\"

class ConsoleOutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        # 这个类必须得有，不然会报错
        pass


class SocketBody:
    def __init__(self, host, port):
        self.headLength = 10
        self.activate = True
        self.Interval = None
        self.CheckPath = None
        self.fileTag = 0
        self.fileName = None
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, port))
            print("Connected Service")
        except Exception as e:
            print(e)
        self.recvData = bytes()
        self.sendMSG("database" + "|" + ' '.join(os.listdir(Path+"database")))
        self.sendMSG("name"+"|"+UserName)
        self.thread = threading.Thread(target=self.receiveMSG)
        self.thread.start()
        self.thread = threading.Thread(target=self.autoScan)
        self.thread.start()

    def sendMSG(self, msg: str):
        body = msg.encode()
        headPack = "0" * (10 - len(str(len(body)))) + str(len(body))
        sendData = headPack.encode() + body
        try:
            self.conn.send(sendData)
        except Exception as e:
            print("sendMSG:", e)

    def receiveMSG(self: socket):
        try:
            while self.activate:
                while len(self.recvData) < self.headLength:
                    self.recvData += self.conn.recv(1024)
                headPack = self.recvData[:self.headLength]
                bodyLength = int(headPack.decode())
                body = self.recvData[self.headLength:]
                while len(body) < bodyLength:
                    if self.fileTag != 0:
                        body += self.conn.recv(1024000)
                    else:
                        body += self.conn.recv(1024)
                self.recvData = body[bodyLength:]
                body = body[:bodyLength]
                self.manipulate(body)
        except Exception as e:
            print("receiveMSG:", e)

    def manipulate(self, body):
        global Path, Interval, CheckPath
        if self.fileTag != 0:
            if self.fileTag == 1:
                with open(Path + "database\\" + self.fileName, "wb+") as f:
                    f.write(body)
            self.fileTag = 0
            return
        body = body.decode()
        body = body.split("|")
        # print(body)
        if body[0] == " ":
            self.sendMSG(" " + "|")
        if body[0] == "changePath":
            Path = body[1]
        if body[0] == "load":
            Interval = self.Interval
            CheckPath = self.CheckPath
            with open("user.config", "r") as file:
                for line in file.readlines():
                    line = line.strip()  # 去除每行两端的空白字符
                    if line and not line.startswith("#"):  # 忽略空行和以#开头的行
                        print(line)
        if body[0] == "del":
            os.remove(Path+"database\\"+body[1])
        if body[0] == "database":
            self.fileTag = 1
            self.fileName = body[1]
        if body[0] == "content":
            self.sendMSG("database" + "|" + ' '.join(os.listdir(Path + "database")))
        if body[0] == "config":
            conf = body[1].split(" ")
            self.Interval = int(conf[0])
            self.CheckPath = conf[1]
            with open("user.config", "w+") as f:
                f.write("Host = "+Host+"\nPort = "+str(Port)+"\nInterval = "+str(self.Interval)\
                        +"\nPath = "+Path+"\nCheckPath = "+self.CheckPath+"\nUserName = "+UserName)
        if body[0] == "scan":
            print("远程服务端病毒查杀")
            res = self.result_Procedure(scan_file_with_clamav())
            if len(res) > 0:
                self.sendMSG("Warning|"+res)
        if body[0] == "shutdown":
            self.__del__()

    def autoScan(self):
        while self.activate:
            time.sleep(Interval*1000)
            res = self.result_Procedure(scan_file_with_clamav())
            print(res)

    def result_Procedure(self, msg):
        msg = scan_file_with_clamav()
        msgList = msg.split("\n")
        virusList = [x for x in msgList if x.__contains__("FOUND")]
        res = ""
        for x in virusList:
            fileText = "FilePath:" + x + "\n" + "FileInformation:"
            xList = x.split(":")
            try:
                with open(xList[0] + ":" + xList[1], "r", encoding="UTF-8") as f:
                    fileTexts = f.readlines()
                for y in fileTexts:
                    fileText += y
            except Exception as e:
                fileText += "This file cannot read, which is maybe as a zip file or others."
            res += fileText + "\n\n"
        return res

    def __del__(self):
        self.sendMSG("shutdown")
        self.conn.shutdown(2)
        self.conn.close()


def scan_file_with_clamav():
    try:
        # 构建完整的clamscan命令，包括递归扫描选项和文件路径
        command = [Path+"clamscan", "--recursive", CheckPath]
        # 执行命令并捕获标准输出和标准错误输出，将结果以字符串形式返回
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        print(f"执行ClamAV扫描时出错: {e}")
        return None


def onDestory():
    try:
        client.__del__()
    except Exception as e:
        print("onDestory:", e)
    finally:
        client.activate = False
        root.destroy()
        exit()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("控制台输出界面")
    root.protocol("WM_DELETE_WINDOW", onDestory)
    text_widget = tk.Text(root)
    text_widget.pack()
    # 重定向标准输出到界面
    redirector = ConsoleOutputRedirector(text_widget)
    sys.stdout = redirector
    try:
        with open("user.config", "r") as file:
            for line in file.readlines():
                line = line.strip()  # 去除每行两端的空白字符
                if line and not line.startswith("#"):  # 忽略空行和以#开头的行
                    print(line)
                    parts = line.split("=")
                    if len(parts) == 2:
                        key = parts[0].strip()  # 去除变量名的空格
                        value = parts[1].strip()  # 去除值的空格
                    if key == "Host":
                        Host = value
                    if key == "Port":
                        Port = int(value)
                    if key == "Interval":
                        Interval = int(value)
                    if key == "Path":
                        Path = value
                    if key == "CheckPath":
                        CheckPath = value
                    if key == "UserName":
                        UserName = value
    except FileNotFoundError:
        print("user.config文件不存在")
    client = SocketBody(Host, Port)
    root.mainloop()
    client.activate = False

