from threading import Event
from queue import Queue
import time

from dialog_manager import DialogManagerHandler

if __name__ == "__main__":
    input_queue = Queue()
    output_queue = Queue()
    import threading
    from rich.console import Console
    from rag_example import RAG

    console = Console()
    stop_event = threading.Event()

    dm = DialogManagerHandler(
        stop_event=stop_event,
        queue_in=input_queue,
        queue_out=output_queue,
        device= "mps",
        rag= RAG
    )

    thread = threading.Thread(target=dm.run)
    thread.start()

    request = "What can you tell me about bankruptcy ?"
    input_queue.put(request)
    console.print(f"[yellow]USER: {request}")
    console.print(f"[green]RAG: {output_queue.get()}")


    # request = "What can you tell me about financial statements ?"
    # console.print(f"[yellow]USER: {request}")
    # input_queue.put(request)
    # console.print(f"[green]RAG: {output_queue.get()}")
    