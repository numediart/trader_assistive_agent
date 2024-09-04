from s2s.s2s_pipeline import S2SPipeline
from ACTHandler import ACTHandler
from queue import Queue

if __name__ == "__main__":
    pipeline = S2SPipeline()

    # actHandler = ACTHandler(
    #     pipeline.stop_event,
    #     queue_in=pipeline.send_audio_chunks_queue,
    #     queue_out=Queue()
    # )
    # actHandler.roomID = "d8a5da3f-5087-4ad5-9f99-547d6484739b"
    # pipeline.act = actHandler

    actHandler = ACTHandler(
        roomID="b0f0c698-04d6-43ae-9888-a7048a4c9c51",
        input_queue=pipeline.comms_handlers[0].output_queue#send_audio_chunks_queue
    )

    pipeline.act = actHandler




    pipeline.run()
