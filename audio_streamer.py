import threading
import sounddevice as sd
import numpy as np

import time
import logging

logger = logging.getLogger(__name__)


class LocalAudioStreamer:
    def __init__(
        self,
        input_queue,
        list_play_chunk_size=512,
    ):
        self.list_play_chunk_size = list_play_chunk_size

        self.stop_event = threading.Event()
        self.input_queue = input_queue

    def start(self):
        def callback(indata, frames, time, status):
            self.input_queue.put(indata.copy())

        logger.debug("Available devices:")
        logger.debug(sd.query_devices())
        with sd.InputStream(
            samplerate=16000,
            dtype="int16",
            channels=1,
            callback=callback,
            blocksize=self.list_play_chunk_size,
        ):
            logger.info("Starting local audio stream")
            while not self.stop_event.is_set():
                time.sleep(0.001)
            print("Stopping recording")
