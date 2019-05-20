# -*- coding=utf8 -*-

#
# 服务调用端
#

import socket
import time
import threading
import selectors
import json

class ServiceClient:
    def __init__(self,serverCenterHost):
        self.centerAddr = serverCenterHost
        self.sel = selectors.DefaultSelector()
        self.apps = {}
        self.conns = {}
        self.initCenter()


    def apiSend(self,appName,data):
        clist = self.apps.get(appName)
        if not clist:
            print("--{}--{}--{}-".format(appName, self.apps, self.apps[appName]))
            return None
        else:

            for addrJson in clist.keys():

                print(addrJson)
                addr = json.loads(addrJson)
                con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                con.connect(tuple(addr))
                con.send(json.dumps(data).encode("utf8"))
                data = con.recv(1024*1024).decode('utf8')
                con.close()
                return json.loads(data)

        return None

    def getConCache(self,appname):
        if not hasattr(self.conns,appname):
            return None
        for addr,val in self.conns[appname].items():
            for con,lock in val.items():
                if not lock:
                    self.conns[appname][addr][con] = True
                    return con
        return None

    def pingServerCenter(self):
        threading.Timer(3,self.pingServerCenter).start()

    def initCenter(self):
        sd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print(self.centerAddr)
        sd.connect(self.centerAddr)

        self.readCender(sd,0)
        sd.setblocking(False)
        self.sel.register(sd,selectors.EVENT_READ,self.readCender)
        threading.Thread(target=self.threadCenter,args=()).start()
    def threadCenter(self):
        while True:
            events = self.sel.select()
            for key,mask in events:
                func = key.data
                func(key.fileobj,mask)
    def readCender(self,sock:socket.socket,mask):
        data = sock.recv(1024*1024)
        if not data:
            sock.close()
        else:
            data = data.decode('utf8')
            if data.startswith('OK'):
                pass
            else:
                self.apps = json.loads(data)

if __name__ == '__main__':
    c = ServiceClient(('127.0.0.1',9003))
    #time.sleep(1)
    d = c.apiSend('AppName',[1])
    print(d)