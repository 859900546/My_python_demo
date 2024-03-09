import _pickle
import pickle
import socket
import time


class TCP:
    def __init__(self, host='0.0.0.0', port=12345, data_length=1307365):
        self.__HOST = host
        self.__PORT = port
        self.__data_length = data_length
        # 创建套接字
        self.__server_socket = None
        self.__client_socket, self.__address = None, None
        self.__infor = None

    def wait_client_socket(self):
        self.__server_socket.listen(1)  # 监听连接
        print('等待客户端连接...')
        self.__client_socket, self.__address = self.__server_socket.accept()  # 连接客户端
        print('连接地址:', self.__address)

    # 绑定主机和端口
    def init(self):
        print("正在初始化socket....")
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
        self.__server_socket.bind((self.__HOST, self.__PORT))  # 绑定ip地址和端口
        print('socket初始化成功')
        self.wait_client_socket()  # 等待客户端连接

    # 接收数据并处理
    def recv_img(self):
        try:
            chunk = self.__client_socket.recv(self.__data_length)  # 读取最大长度，局域网无限制
        except ConnectionResetError:
            self.wait_client_socket()  # 等待客户端连接
            return None
        try:
            arr = pickle.loads(chunk)  # 序列化np
        except:
            return None
        return arr

    def send_point(self, ans):
        data = pickle.dumps(ans)
        try:
            self.__client_socket.sendall(data)  # 发送坐标
        except ConnectionResetError:
            self.wait_client_socket()
            return False
        return True


class UDP:
    def __init__(self, ip='0.0.0.0', port=8608, maxsize=307366, timeout=1):
        self.__IP = ip
        self.__PORT = port
        self.__udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建套接字
        self.__udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, maxsize)  # 设置套接字
        self.__udp_socket.settimeout(timeout)  # 设置超时
        # 绑定地址和端口
        self.__server_address = (self.__IP, self.__PORT)
        self.__udp_socket.bind(self.__server_address)

        self.__address = None  # 地址
        self.loss_data = pickle.dumps([])  # 丢包发送数据
        print("正在启动...")

    def recv_img(self):
        start_time = time.time()  # 初始时间
        add_data = {}  # 保存数据的字典
        wait_client = False  # 判断是否存在连接
        # 分段读取数据流
        while True:
            try:
                data, self.__address = self.__udp_socket.recvfrom(81928)
            except socket.timeout:
                wait_client = True
                break
            sequence = data[0]  # 数据块序号
            length = data[1]  # 数据总长度
            chunk = data[2:]  # 数据块实体
            add_data[sequence] = chunk  # 数据块添加到字典
            if len(add_data) >= length:  # 跳出循环条件
                break
            if time.time() - start_time >= 1:  # 超时处理
                print('丢包')
                return None
        if wait_client:  # 无连接处理
            return None
        img_arr = b''
        # 拼装数据块并序列化字节流
        for i in range(len(add_data)):
            try:
                img_arr += add_data[i]
            except KeyError:
                return []
        try:
            img_arr = pickle.loads(img_arr)
        except:
            return []
        return img_arr

    def send_point(self, ans):
        data = pickle.dumps(ans)  # 逆序数据
        self.__udp_socket.sendto(data, self.__address)

    # 关闭套接字
    def __del__(self):
        self.__udp_socket.close()

