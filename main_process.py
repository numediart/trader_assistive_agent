# RECEIVE DATA FROM QUEUING SYSTEM

# RULES TO DECIDE THE ACTION OF THE AGENT
# 1) RESPOND TO FIAANCE/INVESTING RELATED QUESTIONS => CALL RAG SYSTEM
# 2) SPONTANOUS COMMUNICATION WITH USER WHEN SPECIFIC STATES DETECTED (STRESS, HIGH RISK TRANSACTION REQUEST)
# => BIOSIG INTO PROMPT
# 3) FILL UP A SURVEY WITH THE AVATAR
from s2s.s2s_pipeline import S2SPipeline
from dialog_manager import DialogManagerHandler
from rag_example import RAG

import threading
import time

stop_event = threading.Event()
pipeline = S2SPipeline()
pipeline.lm = DialogManagerHandler(
    stop_event=stop_event,
    queue_in=pipeline.text_prompt_queue,
    queue_out=pipeline.lm_response_queue,
    device= "mps",
    rag= RAG
)

pipeline.run()
time.sleep(5)
pipeline.text_prompt_queue.put("what can you tell me about bankruptcy?")