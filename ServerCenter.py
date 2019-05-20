# -*- coding=utf8 -*-

import logging
import socket
import selectors
import threading
import queue
import json
import time

class Server:
    def __init__(self,port:int):
        self.port = port
        self.cons = {}
        self.apps = {}
        self.sel = selectors.DefaultSelector()
        self.isRun = True
        self.queue = queue.Queue(1024)
        self.checkPing()
        threading.Thread(target=self.udp).start()
        self.tcp()


    def udp(self):
        sd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        sd.bind(('0.0.0.0',self.port))
        while self.isRun:
            msg,addr = sd.recvfrom(1024)
            msg = msg.decode('utf8')
            print(msg,addr)
            data = json.loads(msg)
            self.saveServiceConf(data,addr)
            sd.sendto('OK'.encode('utf8'),addr)

    # 保存服务注册信息
    def saveServiceConf(self,data:dict,addr):
        if not hasattr(self.apps,data['app']):
            self.apps[data['app']] = {}
        key = json.dumps((addr[0],data['port']))
        if not hasattr(self.apps[data['app']],key):
            #全部的链接都增加配置
            self.apps[data['app']][key] = time.time()
            return self.sendAll()
        self.apps[data['app']][key] = time.time()
        print("port{} name {}".format(data['port'],data['app']))

    # 检查服务存活
    def checkPing(self):
        flg = False
        t = time.time()
        for (app,val) in self.apps.items():
            for (addr,ti) in val.items():
                if t - ti > 3:
                    flg = True
                    del self.apps[app][addr]
        if flg:
            self.sendAll()
        threading.Timer(3, self.checkPing).start()

    def tcp(self):
        sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sd.bind(('0.0.0.0', self.port))
        sd.listen(0)
        sd.setblocking(False)
        self.sel.register(sd,selectors.EVENT_READ,self.accept)
        while self.isRun:
            events = self.sel.select()
            for key,mask in events:
                func = key.data
                func(key.fileobj,mask)

    def accept(self,sock:socket.socket,mask):
        con,addr = sock.accept()
        self.cons[con] = addr
        data = json.dumps(self.apps)
        con.send(data.encode('utf8'))
        print("发送配置信息")
        self.sel.register(con,selectors.EVENT_READ,self.read)

    def read(self,sock:socket.socket,mask):
        data = sock.recv(10)
        if not data:
            self.sel.unregister(sock)
            del self.cons[sock]
        else:
            sock.send('OK'.encode('utf8'))

    def sendAll(self):
        data = json.dumps(self.apps)
        print(self.apps,data)
        for con in self.cons.keys():
            con.send(data.encode("utf8"))


if __name__ == '__main__':
    Server(9003)