import time

import cv2
import loguru
import pyautogui
import dxshot
from io import BytesIO


bytes_io = BytesIO()
screen_width, screen_height = pyautogui.size()  # 获取屏幕尺寸
codec = cv2.VideoWriter_fourcc(*"VP90")  # 视频编码器
output_file = "static/screen_share001.WebM"  # 输出视频文件名
fps = 30.0  # 视频帧率
output = cv2.VideoWriter(output_file, codec, fps, (screen_width, screen_height))

begin_time = time.time()

n = 120
while n > 0:
    n -= 1
    img = dxshot.Cp.grab()
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    output.write(img)
    # cv2.imshow("Screen", img)
    if cv2.waitKey(1) == ord("q"):
        break
# output.release()

loguru.logger.info(f"录制完成，耗时：{time.time() - begin_time}秒")
cv2.destroyAllWindows()
