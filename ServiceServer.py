# -*- coding=utf8 -*-

#
# 微服务
#

import threading
import socket
import json
import selectors
import queue

class ServiceServer:
    def __init__(self,appName,port,servercenter):
        self.redata = {}
        self.redata['port'] = port
        self.redata['app'] = appName
        self.port = port
        self.servercenteraddr = servercenter
        self.workerQueue = queue.Queue(1024)
        self.sel = selectors.DefaultSelector()
        self.registerServer()
        self.initThreadPool()
        self.tcp()

    def registerServer(self):
        sd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        print(self.port)
        sd.sendto(json.dumps(self.redata).encode('utf8'),self.servercenteraddr)
        print(sd.recv(1024))
        sd.close()
        threading.Timer(3,self.registerServer).start()

    def tcp(self):
        sd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        sd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sd.bind(('0.0.0.0',self.port))
        sd.listen(-1)
        sd.setblocking(False)
        self.sel.register(sd,selectors.EVENT_READ,self.accept)
        while True:
            events = self.sel.select()
            for key,mask in events:
                print(key)
                func = key.data
                func(key.fileobj,mask)

    def read(self,sock:socket.socket,mask):
        data = sock.recv(4096)
        print(data)
        if data is None:
            self.sel.unregister(sock)
        else:
            self.workerQueue.put((data.decode('utf8') ,sock))

    def accept(self,sock:socket.socket,mask):
        con,addr = sock.accept()
        con.setblocking(False)
        self.sel.register(con,selectors.EVENT_READ,self.read)


    def hadel(self,data,con:socket.socket):
        con.send(json.dumps({"a":"b","list" : [1,2,3,4]}).encode('utf8'))

    def initThreadPool(self):
        for i in range(20):
            t = threading.Thread(target=self.run,args=(self.workerQueue,))
            t.start()


    def run(self,q:queue.Queue):
        while True:
            msg,con = q.get()
            try:
                self.hadel(json.loads(msg),con)
            except Exception as e:
                print(e)
            q.task_done()

if __name__ == '__main__':
    ServiceServer('AppName',9004,('127.0.0.1',9003))