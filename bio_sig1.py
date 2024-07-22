#EXTRACT DATA


#TRANSFER DATA TO QUEUING SYSTEM

'''
queuing system example code
'''
import pika
import time
import json
import random
from datetime import datetime
import threading

def connect_to_rabbitmq():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def generate_sensor_data(sensor_id):
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange='sensors_exchange', exchange_type='fanout')

    while True:
        data = {
            "sensor_id": sensor_id,
            "timestamp": datetime.now().isoformat(),
            "data": random.choice([
                "text message",
                random.randint(0, 100),
                [random.randint(0, 10) for _ in range(5)]
            ])
        }
        message = json.dumps(data)
        try:
            channel.basic_publish(exchange='sensors_exchange', routing_key='', body=message)
            print(f" [x] Sent {message}")
        except pika.exceptions.AMQPError as e:
            print(f"Failed to send message: {e}")
        time.sleep(random.randint(1, 5))

    # Fermeture de la connexion (ce code ne sera jamais atteint dans la boucle infinie)
    connection.close()

if __name__ == "__main__":
    sensor_ids = ['sensor_1', 'sensor_2', 'sensor_3']
    threads = []

    for sensor_id in sensor_ids:
        thread = threading.Thread(target=generate_sensor_data, args=(sensor_id,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
