# region 头文件
import pickle
import socket


class TCP:
    def __init__(self, ip, port):
        self.HOST = ip
        self.PORT = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_server(self):
        try:
            self.client_socket.connect((self.HOST, self.PORT))
        except:
            print('连接失败')
        print("连接成功")

    def send_img(self, img):
        data = pickle.dumps(img)
        self.client_socket.sendall(data)

    def get_point(self, img):
        data = pickle.dumps(img)
        self.client_socket.sendall(data)
        response = self.client_socket.recv(60)
        try:
            ans = pickle.loads(response)
        except:
            return []
        return ans

    def __del__(self):
        self.client_socket.close()


class UDP:
    def __init__(self, ip='192.168.2.146', port=8608, chunk_size=64997):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 5007366)
        self.udp_socket.settimeout(0.1)
        # print(udp_socket.s)
        self.__IP = ip
        self.__PORT = port
        self.server_addres = (self.__IP, self.__PORT)
        self.chunk_size = chunk_size

    def send_img(self, img):
        data = pickle.dumps(img)
        sequence = 0
        chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        for chunk in chunks:
            self.udp_socket.sendto(bytes([sequence]) + bytes([len(chunks)]) + chunk, self.server_addres)
            sequence += 1

    def get_ponit(self, img):
        data = pickle.dumps(img)
        sequence = 0
        chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        for chunk in chunks:
            self.udp_socket.sendto(bytes([sequence]) + bytes([len(chunks)]) + chunk, self.server_addres)
            sequence += 1
        try:
            data, addres = self.udp_socket.recvfrom(100)
        except socket.timeout:
            return []
        try:
            data = pickle.loads(data)
        except:
            return []
        return data

    def __del__(self):
        self.udp_socket.close()
