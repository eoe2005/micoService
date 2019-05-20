# micoService
Python微服务框架

# 服务配置服务器
    ServerCenter.py

`Server(9003)`

启动后代码会监听 9003 的udp 和 tcp 端口
+ udp 负责服务注册 服务提供者每个3秒注册一次，每当有变化，或者超过3秒没有注册，将会把新的配置信息下发到所有的客户端
+ tcp 负责服务发现 ，客户端在调用微服务前都要先练级该中心服务器，获取配置信息，3秒发一次心跳包

# 微服务
    serviceServer.py
## 使用
    
    class testservice(ServiceServer):
        def hadel(self,data,con:socket.socket): 处理业务请求
    

    默认会创建一个20个线程的线程池，每次都用线程池处理请求

## 服务启动

    ServiceServer('AppName',9004,('127.0.0.1',9003))
    
    第一个参数是服务名字，
    第二个参数是服务要监听的端口
    第三参数是中心配置服务器的ip和端口


# 客户端
    Client.py
## 使用

    c = ServiceClient(('127.0.0.1',9003))
    参数是中心配置服务的ip和断开

    d = c.apiSend('AppName',[1])
    向 AppName 服务发送请求，参数是 [1] 返回结果是JSON解析后的对象
    