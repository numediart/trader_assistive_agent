from s2s.baseHandler import BaseHandler
import logging

logger = logging.getLogger(__name__)

remove_list = [str(i)+"." for i in range(10)]

class DialogManagerHandler:
    def __init__(
            self,
            stop_event,
            queue_in,
            queue_out,
            device="cpu",
            rag=None
    ):
        self.stop_event = stop_event
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.device = device
        self.rag=rag
        self.warmup()

    def warmup(self):
        logger.info(f"Warming up {self.__class__.__name__}")
        dummy_input = "Is that a question?"
        n_steps = 1
        for _ in range(n_steps):
            _ = self.rag.retrieve_answer(dummy_input)
        
    def run(self):
        while not self.stop_event.is_set():
            prompt = self.queue_in.get()
            text_type = "question" if prompt.endswith("?") else "prompt"
            if text_type == "question":
                generated_text = self.rag.retrieve_answer(prompt)
                self.queue_out.put(generated_text)

            elif text_type == "prompt":
                # request spontaneous answer
                answer = "chill dude..."
                self.queue_out.put(answer)