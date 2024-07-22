import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f" [x] Received {message}")

def receive_bio_sigs():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Déclaration de l'échange
    channel.exchange_declare(exchange='sensors_exchange', exchange_type='fanout')

    # Déclaration d'une file d'attente anonyme
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Liaison de la file d'attente à l'échange
    channel.queue_bind(exchange='sensors_exchange', queue=queue_name)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    receive_bio_sigs()
