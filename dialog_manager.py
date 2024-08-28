from s2s.baseHandler import BaseHandler
import logging

logger = logging.getLogger(__name__)

class DialogManagerHandler(BaseHandler):
    def setup(
            self, 
            device="cpu",
            rag=None,
            prompt_creator=None
    ):
        self.device = device
        self.rag=rag
        self.prompt_creator=prompt_creator
        self.warmup()

    def warmup(self):
        logger.info(f"Warming up {self.__class__.__name__}")
        _ = self.choice["question"]
        
    def process(self, prompt):
        prompt = prompt.decode("utf-8")
        text_type = "question" if prompt.endswith("?") else "prompt"

        if text_type == "question":
            answer = self.rag.retrieve_answer(
                prompt
            )

        elif text_type == "prompt":
            # request spontaneous answer
            answer = "chill dude..."

        yield answer