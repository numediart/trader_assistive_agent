# RECEIVE DATA FROM QUEUING SYSTEM

# RULES TO DECIDE THE ACTION OF THE AGENT
# 1) RESPOND TO FIAANCE/INVESTING RELATED QUESTIONS => CALL RAG SYSTEM
# 2) SPONTANOUS COMMUNICATION WITH USER WHEN SPECIFIC STATES DETECTED (STRESS, HIGH RISK TRANSACTION REQUEST)
# => BIOSIG INTO PROMPT
# 3) FILL UP A SURVEY WITH THE AVATAR
from queue import Queue
import threading

from audio_streamer import LocalAudioStreamer
from VAD.vad import VAD
from ASR.lightning_whisper_mlx import LightningWhisperASR
from dialog_manager import DialogManagerHandler
from TTS.melo import MeloTTS
from rag_example import RAG

import matplotlib.pyplot as plt
import numpy as np

should_listen = threading.Event()
should_listen.set()

rcv_audio_chuncks_queue = Queue()
send_audio_chuncks_queue = Queue()

local_audio_streamer = LocalAudioStreamer(input_queue=rcv_audio_chuncks_queue, output_queue=send_audio_chuncks_queue)
vad = VAD(should_listen)
asr = LightningWhisperASR(device="mps")
dm = DialogManagerHandler(rag=RAG)
tts = MeloTTS(should_listen)

blocksize = 512

thread = threading.Thread(target=local_audio_streamer.start)
thread.start()
print("started recording")
while True:
    vad.should_listen = should_listen
    mic_data = local_audio_streamer.input_queue.get()
    spoken_prompt_queue = vad.process(mic_data)
    should_listen = vad.should_listen
    if spoken_prompt_queue is not None and not should_listen.is_set():
        # ASR
        prompt = asr.process(spoken_prompt_queue)
        
        # do Dialog Manager
        dm_output = dm.process(prompt)

        # TTS
        audio_output = tts.process(dm_output)
        for i in range(0, len(audio_output), blocksize):
            local_audio_streamer.output_queue.put(np.pad(
                audio_output[i : i + blocksize],
                (0, blocksize - len(audio_output[i : i + blocksize])),
            ))
        should_listen = tts.should_listen
        