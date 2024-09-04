import logging

logger = logging.getLogger(__name__)

class DialogManagerHandler:
    def __init__(
            self, 
            device="cpu",
            rag=None,
            prompt_creator=None
    ):
        self.device = device
        self.rag=rag
        self.prompt_creator=prompt_creator
        
    def process(self, prompt):
        text_type = "question" if prompt.endswith("?") else "prompt"

        if text_type == "question":
            answer = self.rag.retrieve_answer(
                prompt
            )

        elif text_type == "prompt":
            # request spontaneous answer
            answer = "chill dude..."

        return answer