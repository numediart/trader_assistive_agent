from s2s.baseHandler import BaseHandler

import datetime
import websocketClient
from io import BytesIO
import base64
from pydub import AudioSegment
import time
import sounddevice as sd

import io

import numpy as np
from s2s.utils.utils import int2float
import soundfile as sf
import threading

class ACTHandler:
    def __init__(
        self,
        roomID,
        input_queue
    ):
        self.input_queue = input_queue
        self.stop_event = threading.Event()
        self.roomID = roomID
        # self.client = websocketClient.websocketClient("ws://localhost:9001", debug=False)

    def run(self):
        def callback(indata, outdata, frames, time, status):
            # self.input_queue.put(indata.copy())
            # outdata[:] = 0 * outdata
            # print(indata)
            # print((len(indata), len(outdata)))
            # print(indata)
            timestamp = datetime.datetime.now().timestamp()
            sf.write("test{}.wav".format(timestamp), indata, 16000)

        with sd.Stream(
            samplerate=16000,
            dtype="int16",
            channels=1,
            callback=callback,
            blocksize=512*100,
        ):

            while not self.stop_event.is_set():
                time.sleep(0.001)
        # audio_chunk = self.input_queue.get()
        # print(audio_chunk)
        # audio_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
        # print(audio_int16)
        # audio_float32 = int2float(audio_int16)
        # print(audio_float32)
        # timestamp = datetime.datetime.now().timestamp()
        # sf.write("test-audiochunk-{}.wav".format(timestamp), audio_chunk, 16000)
        # sf.write("test-audio_int16-{}.wav".format(timestamp), audio_int16, 16000)
        # sf.write("test-audio_float32-{}.wav".format(timestamp), audio_float32, 16000)


        # buffer = io.BytesIO()
        # sf.write(buffer, audio_float32, 16000, format='WAV')
        # wav_data = buffer.getvalue()
        # buffer.close()
        # timestamp = datetime.datetime.now().timestamp()
        # sf.write("test{}.wav".format(timestamp), audio_chunk, 16000)
        # bytes_recorded = len(wav_data)
        # buffer_base64 = base64.b64encode(wav_data).decode('utf-8')
        # data = {
        #     "timestamp": timestamp,
        #     "buffer": buffer_base64,
        #     "bytesRecorded": bytes_recorded,
        #     "sampleRate": 16000,
        #     "roomId": self.roomID
        # }
        # # Send the payload to the server
        # self.client.send("EmitAudioData", data)
        # while not self.stop_event.is_set():
        #     time.sleep(0.001)


# class ACTHandler(BaseHandler):
#     def setup(
#         self
#     ):
#         self.roomID = ""
#         self.client = websocketClient.websocketClient("ws://localhost:9001", debug=False)
#
#     def process(self, audio_chunk):
#         audio_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
#         audio_float32 = int2float(audio_int16)
#
#
#         buffer = io.BytesIO()
#         sf.write(buffer, audio_float32, 16000, format='WAV')
#         wav_data = buffer.getvalue()
#         buffer.close()
#         timestamp = datetime.datetime.now().timestamp()
#         sf.write("test{}.wav".format(timestamp), audio_chunk, 16000)
#         bytes_recorded = len(wav_data)
#         buffer_base64 = base64.b64encode(wav_data).decode('utf-8')
#         data = {
#             "timestamp": timestamp,
#             "buffer": buffer_base64,
#             "bytesRecorded": bytes_recorded,
#             "sampleRate": 16000,
#             "roomId": self.roomID
#         }
#         # Send the payload to the server
#         self.client.send("EmitAudioData", data)
#         yield None
