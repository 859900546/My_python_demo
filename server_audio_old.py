import queue
import socket
import threading
import time

import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100


def findInternalRecordingDevice(p, target='立体声混音'):
    # 要找查的设备名称中的关键字
    # 逐一查找声音设备
    for i in range(p.get_device_count()):
        devInfo = p.get_device_info_by_index(i)
        if devInfo['name'].find(target) >= 0 and devInfo['hostApi'] == 0:
            # print('已找到内录设备,序号是 ',i)
            return i
    print('无法找到内录设备!')
    return -1


p = pyaudio.PyAudio()
# 查找内录设备
dev_idx = findInternalRecordingDevice(p)
# 在打开输入流时指定输入设备
in_stream = p.open(input_device_index=dev_idx,
                   format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 5007366)
udp_socket.settimeout(0.1)
# print(udp_socket.s)
__IP = '10.22.186.159'
# __IP = '0.0.0.0'
# __IP = '192.168.3.81'
__PORT = 6618
server_addres = (__IP, __PORT)
# udp_socket.bind(server_addres)

# # 缓存区配置
# buffer = queue.Queue()
# buffer_set = set()
#
# # 连接集合配置
# connect_set = set()


def record():
    # 循环读取输入流
    while True:
        data = in_stream.read(CHUNK)
        yield data
        # print(data)
        # out_stream.write(data)
        # yield data


# def start():
#     global Now_data
#     print(f'正在监听：{__IP}地址')
#     for i in record():
#         buffer.put(i)


def thread_():
    while True:
        data = in_stream.read(CHUNK)
        udp_socket.sendto(data, server_addres)
    #  time.sleep(max(0.03 - time.time() + s, 0))


thread_()
