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

should_listen = threading.Event()
should_listen.set()

rcv_audio_chuncks_queue = Queue()

local_audio_streamer = LocalAudioStreamer(input_queue=rcv_audio_chuncks_queue)
vad = VAD(should_listen)

thread = threading.Thread(target=local_audio_streamer.run)
thread.start()
print("started recording")
while True:
    if spoken_prompt_queue.not_empty:
        pass
        # do ASR    spoken_prompt_queue = vad.process(mic_data)
    if spoken_prompt_queue is not None:
        # do Dialog Manager