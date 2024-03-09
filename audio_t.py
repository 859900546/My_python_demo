import io
import os
import queue
import threading
import time
import wave
from io import BytesIO

import loguru
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
# 在打开输入流时指定输入设备
in_stream = p.open(input_device_index=dev_idx,
                   format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK)


# wf = wave.open("output.wav", 'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)


# 将音频数据写入编码器


# vorbis_encoder = pyogg.VorbisEncoder(channels, sample_rate, quality=3)


def record():
    # 循环读取输入流
    while True:
        my_buf = []
        n = 300
        output_stream = BytesIO()
        while n > 0:
            n -= 1
            data = in_stream.read(CHUNK)
            my_buf.append(data)
        with wave.open(output_stream, 'wb') as wf:
            wf.setnchannels(CHANNELS)  # 单声道
            wf.setsampwidth(2)  # 2 字节
            wf.setframerate(RATE / 2)
            # wf.setcomptype("NONE", "ULAW")
            # wf.setnframes(len(data))
            # wf.setcomptype('NONE', 'not compressed')
            # 将音频数据写入 WAV 文件
            wf.writeframes(b''.join(my_buf))
        wav_byte_stream = output_stream.getvalue()
        yield wav_byte_stream
        # yield wav_byte_stream


buffer = queue.Queue(maxsize=2)


def test():
    while True:
        # print(f'buffer--{buffer.qsize()}')
        if buffer.qsize() > 0:
            yield buffer.get()
        else:
            time.sleep(0.002)
            continue


begin = time.time()
audio_list = []


def thread_audio_2(my_buf):
    global begin
    output_stream = BytesIO()
    with wave.open(output_stream, 'wb') as wf:
        wf.setnchannels(CHANNELS)  # 单声道
        wf.setsampwidth(2)  # 2 字节
        wf.setframerate(RATE)
        wf.writeframes(b''.join(my_buf))
    # wav_byte_stream = output_stream.getvalue()
    audio = AudioSegment.from_file(output_stream, format="wav")
    output_bytes = BytesIO()
    # # 导出为AAC格式
    audio.export(output_bytes, format="ogg")
    # os._exit(0)
    # # break
    # # 将光标重新设置到起始位置，以便后续操作能够读取输出的BytesIO对象
    wav_byte_stream = output_bytes.getvalue()
    # audio_list.append((audio, time.time() - begin))
    begin = time.time()
    if buffer.qsize() == 2:
        buffer.get()
    buffer.put(wav_byte_stream)


def thread_read_audio():
    while True:
        # nn -= 1
        my_buf = []
        n = 500
        while n > 0:
            n -= 1
            data = in_stream.read(CHUNK)
            my_buf.append(data)
        # print(time.time()-s)
        threading.Thread(target=thread_audio_2, args=(my_buf,)).start()
    # loguru.logger.info('thread_read_audio end')
    # time.sleep(2)
    # loguru.logger.info('play_audio')
    # s = audio_list[0][0]
    # for i in audio_list:
    #     # s = time.time()
    #     # play(i[0])
    #     # print(time.time() - s, audio_list.index(i))
    #     if audio_list.index(i) == 0:
    #         continue
    #     s += i[0]
    # t = time.time()
    # play(s)
    # loguru.logger.info(time.time() - t)
    # loguru.logger.info('play_audio end')
    # # time.sleep(i[1])


# thread_read_audio()
threading.Thread(target=thread_read_audio).start()