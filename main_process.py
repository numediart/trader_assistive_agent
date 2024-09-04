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


should_listen = threading.Event()
should_listen.set()

rcv_audio_chuncks_queue = Queue()

local_audio_streamer = LocalAudioStreamer(input_queue=rcv_audio_chuncks_queue)
vad = VAD(should_listen)
asr = LightningWhisperASR(device="mps")
dm = DialogManagerHandler(rag=RAG)
tts = MeloTTS(should_listen)


thread = threading.Thread(target=local_audio_streamer.start)
thread.start()
print("started recording")
while True:
    vad.should_listen = should_listen
    mic_data = local_audio_streamer.input_queue.get()
    spoken_prompt_queue = vad.process(mic_data)
    should_listen = vad.should_listen
    if spoken_prompt_queue is not None and not should_listen.is_set():
        prompt = asr.process(spoken_prompt_queue)
        
        # do Dialog Manager
        dm_output = dm.process(prompt)

        audio_output = tts.process(dm_output)
        should_listen = tts.should_listen
        