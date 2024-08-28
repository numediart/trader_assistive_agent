from s2s.baseHandler import BaseHandler
from rag_utils import rag_utils as rag
import logging

logger = logging.getLogger(__name__)

class DialogManagerHandler(BaseHandler):
    def setup(
            self, 
            device="cpu",
            rag_retriever=None,
            rag_model=None,
            prompt_creator=None
    ):
        self.device = device
        self.choice = {"question": "answer", "prompt": "chill dude..."}
        self.rag_retriever=rag_retriever
        self.rag_model = rag_model
        self.prompt_creator=prompt_creator
        self.warmup()

    def warmup(self):
        logger.info(f"Warming up {self.__class__.__name__}")
        _ = self.choice["question"]
        
    def process(self, prompt):
        prompt = prompt.decode("utf-8")
        text_type = "question" if prompt.endswith("?") else "prompt"
        if text_type == "question":
            answer = rag.retrieve_answer(
                prompt, 
                self.rag_retriever,
                self.rag_model
            )

        elif text_type == "prompt":
            # request spontaneous answer
            answer = "chill dude..."
            pass

        yield answer