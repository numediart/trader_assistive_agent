import websocket


class websocketClient:
    """
    This class is used to create a websocket client to send data to the server
    """

    def __init__(self, server_address, debug=False):
        """
        This function is used to initialize the websocket client and connect to the server address
        :param server_address:
        :param debug:
        """
        self.server_address = server_address
        self.ws = websocket.WebSocket()
        self.ws.connect(url=server_address)
        self.debug = debug
        if self.debug:
            websocket.enableTrace(True)

    def send(self, event_name: str, data: object):
        """
        This function is used to send data to the server in the form of a json object.
        :param event_name:
        :param data:
        :return:
        """
        try:
            self.ws.send(f'{{"EventName": "{event_name}", "Data": {data}}}')
            if self.debug:
                print(f"[DEBUG] -> Data Sent: {data}")
        except Exception as e:
            print(f"Error while sending data: {e}")

    def close(self):
        """
        This function is used to close the websocket connection
        """
        self.ws.close()
        print("Connection closed")
