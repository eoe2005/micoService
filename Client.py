# -*- coding=utf8 -*-

#
# 服务调用端
#

import socket
import time
import threading


class ServiceClient:
    def __init__(self,serverCenterHost):
        pass

    def apiSend(self,appName,data):
        pass

    def pingServerCenter(self):
        threading.Timer(3,self.pingServerCenter).start()