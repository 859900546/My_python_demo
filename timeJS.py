import cv2
import numpy as np
from ctypes import windll
import os
from mss import mss

os.getcwd()
os.add_dll_directory(os.path.abspath(os.path.dirname(__file__)))
windll.winmm.timeBeginPeriod(1)
stop = windll.kernel32.Sleep

ScreenX = 1920
ScreenY = 1080
fovx = 1920
fovy = 1080
window_size = (
    0,
    0,
    1920,
    1080)


# 定义截图范围 (左上角X，左上角Y，右下角X，右下角Y)
def resize():
    global window_size
    window_size = (
        int(ScreenX / 2 - fovx),
        int(ScreenY / 2 - fovy),
        int(ScreenX / 2 + fovx),
        int(ScreenY / 2 + fovy))


# 实例化mss
Screenshot_value = mss()


def screenshot():
    img = Screenshot_value.grab(window_size)  # 调用mss的方法截图
    img = np.array(img)  # 转换成numpy数组
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # 图片4通道转3通道
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


# import ctypes
# import cv2
# import numpy as np
# from ctypes.wintypes import DWORD, LONG, WORD
#
#
# class BITMAPINFOHEADER(ctypes.Structure):
#     _fields_ = [
#         ("biSize", DWORD),
#         ("biWidth", LONG),
#         ("biHeight", LONG),
#         ("biPlanes", WORD),
#         ("biBitCount", WORD),
#         ("biCompression", DWORD),
#         ("biSizeImage", DWORD),
#         ("biXPelsPerMeter", LONG),
#         ("biYPelsPerMeter", LONG),
#         ("biClrUsed", DWORD),
#         ("biClrImportant", DWORD),
#     ]
#
#
# class BITMAPINFO(ctypes.Structure):
#     _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", DWORD * 3)]
#
#
# Gdi32 = ctypes.windll.gdi32
# User32 = ctypes.windll.user32
#
#
# class capture:
#
#     def __init__(self, x, y, width, height, j):
#         self.x = int(x / 2 - width / 2)
#         self.y = int(y / 2 - height / 2)
#         self.width = width
#         self.height = height
#         self.hwin = User32.FindWindowW(j, None)
#         self.srcdc = User32.GetDC(self.hwin)
#         self.memdc = Gdi32.CreateCompatibleDC(self.srcdc)
#         self.bmi = BITMAPINFO()
#         self.bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
#         self.bmi.bmiHeader.biPlanes = 1
#         self.bmi.bmiHeader.biBitCount = 32
#         self.bmi.bmiHeader.biWidth = width
#         self.bmi.bmiHeader.biHeight = -height
#         self._data = ctypes.create_string_buffer(width * height * 4)
#         self.bmp = Gdi32.CreateCompatibleBitmap(self.srcdc, width, height)
#         Gdi32.SelectObject(self.memdc, self.bmp)
#
#     def cap(self):
#         Gdi32.BitBlt(self.memdc, 0, 0, self.width, self.height, self.srcdc, self.x, self.y, 0x00CC0020)
#         Gdi32.GetDIBits(self.memdc, self.bmp, 0, self.height, self._data, self.bmi, 0)
#         self.p = np.frombuffer(self._data, dtype='uint8').reshape(self.height, self.width, 4)
#
#         Gdi32.DeleteObject(self.bmp)
#         return cv2.cvtColor(self.p, cv2.COLOR_BGRA2BGR)
#
#
# gw = capture(ScreenX, ScreenY, fovx, fovy, None)
#
#
# def wincap():
#     return gw.cap()
#
#
# 把DXGI.pyd 复制到当前路径
# import DXGI

# g = DXGI.capture(0, 0, 1920, 1080)  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)


# def jt_shuaxin():
#     global g, gw, window_size
#     gw = capture(ScreenX, ScreenY, fovx, fovy, None)
#     window_size = (
#         int(ScreenX / 2 - fovx),
#         int(ScreenY / 2 - fovy),
#         int(ScreenX / 2 + fovx),
#         int(ScreenY / 2 + fovy))

#
# def dxgi():
#     img = g.cap()
#     return img


# def show_screenshot():
#     img = dxgi()
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     return img
