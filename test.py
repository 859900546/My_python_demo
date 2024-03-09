import wave
from io import BytesIO

import pyaudio
from pydub import AudioSegment
from pydub.playback import play

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
# print(p.get_default_input_device_info())
# 在打开输入流时指定输入设备
in_stream = p.open(input_device_index=dev_idx,
                   format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK)

output_stream = BytesIO()
# my_buf = []
count = 1  #

# while True:
#     data = in_stream.read(CHUNK)
#     count += 1
#     my_buf.append(data)
#     if count % 1000 == 0:
#         with wave.open('output_stream.wav', 'wb') as wf:
#             wf.setnchannels(2)  # 单声道
#             wf.setsampwidth(2)  # 2 字节
#             wf.setframerate(44100)
#             #  wf.setnframes(len(my_buf))
#             # wf.setcomptype('NONE', 'not compressed')
#             # 将音频数据写入 WAV 文件
#             wf.writeframes(b''.join(my_buf))
#         # wav_byte_stream = output_stream.getvalue()
#         break
#         audio = AudioSegment.from_wav(BytesIO(wav_byte_stream))
#         # 播放音频
#         play(audio)

while True:
    my_buf = []
    n = 500
    while n > 0:
        n -= 1
        data = in_stream.read(CHUNK)
        my_buf.append(data)
    with wave.open(output_stream, 'wb') as wf:
        wf.setnchannels(2)  # 单声道
        wf.setsampwidth(2)  # 2 字节
        wf.setframerate(44100)
        # wf.setnframes(len(my_buf))
        # wf.setcomptype('NONE', 'not compressed')
        # 将音频数据写入 WAV 文件
        wf.writeframes(b''.join(my_buf))
    wav_byte_stream = output_stream.getvalue()
    with wave.open("output_stream.wav", 'wb') as wf:
        wf.setnchannels(2)# 单声道
        wf.setsampwidth(2)  # 2 字节
        wf.setframerate(44100)
        wf.writeframes(wav_byte_stream)
    break
    # audio = AudioSegment.from_wav(BytesIO(wav_byte_stream))
    # # 播放音频
    # play(audio)
