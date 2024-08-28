from threading import Event
from queue import Queue

from dialog_manager import DialogManagerHandler

if __name__ == "__main__":
    input_queue = Queue()
    output_queue = Queue()
    import threading
    from rich.console import Console
    from rag_example import RAG

    console = Console()

    dm = DialogManagerHandler(
        stop_event=Event(),
        queue_in=input_queue,
        queue_out=output_queue,
        setup_kwargs={"device": "mps", "rag": RAG}
    )

    thread = threading.Thread(target=dm.run)

    try:
        thread.start()
        request = b"What can you tell me about bankruptcy ?"
        console.print(f"[yellow]USER: {request.decode('utf-8')}")
        input_queue.put(request)
        console.print(f"[green]RAG: {output_queue.get()}")
        request = b"What can you tell me about financial statements ?"
        console.print(f"[yellow]USER: {request.decode('utf-8')}")
        input_queue.put(request)
        console.print(f"[green]RAG: {output_queue.get()}")

    except KeyboardInterrupt:
        thread.stop()
    