import socket
import threading
BUFSIZE = 100
#import logging


class DataStreamer(object):

    def __init__(self,network, port, Wave_Data_Class, channel):    # Wave_Data_Class here is the instance if the Wave_Data server class
        thread = threading.Thread(name="DataStreamer_Thread", target=self.run)
        thread.daemon = True

        #logging.basicConfig(filename="Logs/Data_streamer.log", level=logging.DEBUG)

        self.Wave_Data = Wave_Data_Class  # instance of the wave data server class
        self.temp_iterator = 1
        self.channel = channel

        self.streaming_status = True
        self.network = network
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        thread.start()

    def send_data(self, data):
        self.sock.sendto(data.encode('utf-8'), (self.network, self.port))

    def set_streaming_status(self, status=True):
        self.streaming_status = status

    def run(self):
        while True:
            if self.streaming_status:
                if self.temp_iterator != self.Wave_Data.wave_iterator:

                    self.temp_iterator = self.Wave_Data.wave_iterator
                    wave_point_voltage = self.Wave_Data.get_wave_data(self.channel)
                    #logging.debug(f"{wave_point_voltage} is wave point voltage \n")

                    try:
                        data = wave_point_voltage[self.temp_iterator-1]
                        header_iterator = str(self.temp_iterator-1)+':'
                        self.send_data(header_iterator+str(data)) # grab the value of the updated point in the array
                        #logging.debug(f'\nself.send_data {header_iterator+str(data)}')
                    except Exception as e:
                        pass
                        #logging.debug(f'\n The sending error was {str(e)}')

class DataReceiver(object):
    def __init__(self, interface, port):
        thread = threading.Thread(name="DataReceiver_Thread",target=self.run)
        thread.daemon = True

        #logging.basicConfig(filename="Logs/Data_Receiver.log", level=logging.DEBUG)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((interface, port))
        self.received_data = None
        self.receiving_status = True

        thread.start()

    def get_received_data(self):
        return self.received_data

    def set_receiving_status(self, status=True):
        self.receiving_status = status
        if status is False:
            self.received_data = 'Stopped'
        elif status is True:
            self.received_data = 'Running'

    def run(self):
        while True:
            if self.receiving_status:
                data, address = self.sock.recvfrom(BUFSIZE)
                message = data.decode('utf-8')
                #logging.debug(f'from thread {message}')
                if message:
                    self.received_data = message



