import socket
import select
import re
#import logging
try:
    import cPickle as pickle
except:
    import pickle

from scpi.scpiLogic.all_fsm import *
from data.Server_Wave_Data import Wave_Data
from data.data_streaming import DataStreamer
from data.data_query import DataQuery

#logging.basicConfig(filename="Logs/server_log.log", level=logging.DEBUG)

HEADERSIZE = 10
IP = "127.0.0.1"
PORT = 1234

STREAM_PORT = 4646

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

clients = {}
client_protocol = {}

# ---------- start the date generation thread ------------
Data_thread = Wave_Data()
# ---------------------------------------------------------

# ---------- start data streaming thread ------------------
Streamer = DataStreamer(IP, STREAM_PORT, Data_thread, 1)   # ip_address, Port, Data_generator_instance, channel
Wdata = None   # Stores the data returned after the date query is made

D_Query = DataQuery(Chan, Mode, Format, Sampling, Data_thread)
wav_start = 120
wav_stop = 1
rst_stats = False
cls_status = False

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADERSIZE)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {"Header":message_header, "data":client_socket.recv(message_length)}
    except:
        return False

def commands(cmd, protocol):
    protocol = protocol['data'].decode('utf-8')

    cmd = cmd.decode('utf-8')

    if protocol.upper() == 'L':
        query = parse_long(cmd, protocol.upper()) #if the cmd was a query, then the returned value is captured
    else:
        query = parse_short(cmd, protocol.upper()) #if the cmd was a query, then the returned value is captured

    return query

def parse_long(cmd, protocol):
    waveform_query = re.compile(':WAveform:\w+\?', re.IGNORECASE)
    waveform_com = re.compile(':WAveform:\w+ \w+', re.IGNORECASE)
    global rst_stats
    global cls_status

    if(waveform_com.match(cmd)):
        print(f'{cmd} is the command ')
        com, parameter = cmd.split(None, 1)
        type = com.split(':')[2]
        #logging.info(f'cmd is {cmd}, com is {com}, param is {parameter} type is {type}')
        if type.upper() == 'SOURCE':
            error = Chan.run(parameter, protocol) # Running 'run' function of the object while also logging any error that is returned
            if error is not None:
                print(error)  # If state temporarily went to error state, print the returned message
                return error
            print(f'{Chan.get_state()} is the current channel selected')
        elif type.upper() == 'MODE':
            error = Mode.run(parameter, protocol)
            if error is not None:
                print(error)  # If state temporarily went to error state, print the returned message
                return error
            print(f'{Mode.get_state()} is the current state of mode')
        elif type.upper() == 'FORMAT':
            error = Format.run(parameter, protocol)
            if error is not None:
                print(error)
                return error
            print(f'{Format.get_state()} is the currnet state of format')
        elif type.upper() == 'START':
            status =Data_thread.set_start(parameter, Mode.get_state())
            if status is False:
                return f"Point out of range for mode {Mode.get_state()}"
        elif type.upper() == 'STOP':
            status = Data_thread.set_stop(parameter, Mode.get_state())
            if status is False:
                return f"Point out of range for mode {Mode.get_state()}"
        else:
            print('Waveform command not found')
            return 'Waveform command not found'
    elif waveform_query.match(cmd):
        print(f'{cmd} is the query')
        type = cmd.split(':')[2]
        #logging.info(f'cmd is {cmd},  type is {type}')
        if type.upper() == 'SOURCE?':
            print(Chan.get_state())
            return Chan.get_state()
        elif type.upper() == 'MODE?':
            print(Mode.get_state())
            return Mode.get_state()
        elif type.upper() == 'FORMAT?':
            print(Format.get_state())
            return Format.get_state()
        elif type.upper() == 'DATA?':
            global Wdata
            Wdata = D_Query.data_query()
            if rst_stats is not False and cls_status is not False:
                return 'Data'
            else:
                return "Use the commands *RST and *CLS before returning data"
        elif type.upper() == 'START?':
            return Data_thread.get_start()
        elif type.upper() == 'STOP?':
            return Data_thread.get_stop()
        elif type.upper() == 'XINCREMENT?':
            return Data_thread.get_xinc(Chan.get_state(), Mode.get_state())
        elif type.upper() == 'XORIGIN?':
            return Data_thread.get_xorg()
        elif type.upper() == 'XREFERENCE?':
            return Data_thread.get_xref()
        elif type.upper() == 'YINCREMENT?':
            return Data_thread.get_yinc()
        elif type.upper() == 'YORIGIN?':
            return Data_thread.get_yorg()
        elif type.upper() == 'YREFERENCE?':
            return Data_thread.get_yref()
        elif type.upper() == 'PREAMBLE?':
            return preamble()
        else:
            print('Waveform query not found') # server side debugging
            return 'Waveform query not found' # client side error message
    elif cmd.upper() == ':RUN' or cmd.upper() == ':STOP':
        #logging.info(f'cmd is {cmd} from run')
        if cmd.upper() == ':RUN':
            if Mode.get_state() != "RAW":
                Data_thread.set_wave_generation_state(True)
                Streamer.set_streaming_status(True)
            else:
                return "Turn off the RAW mode before running the sampler"
        else:
            Data_thread.set_wave_generation_state(False)
            Streamer.set_streaming_status(False)
        Sampling.run(cmd, protocol)
    elif cmd.upper() == '*RST':
        Mode.run('NORM', protocol)  #reset to default
        Chan.run('CHAN1', protocol)
        Format.run('BYTE', protocol)
        rst_stats = 1
        return "Everything has been set to default \n Mode: NORM \n Channel: CHAN1 \n Format: BYTE"
    elif cmd.upper() == '*CLS':
        cls_status = 1
        return "All Event Registers have been cleared"
    else:
        #logging.info(f'cmd is {cmd} from else')
        print('########################')
        print("Command not found, make sure you are sticking to the chosen protocol")
        return f"'{cmd}' Command not found, make sure you are sticking to the chosen protocol"

def parse_short(cmd,protocol):
    waveform_com = re.compile(':WAV:\w+ \w+', re.IGNORECASE)
    waveform_query = re.compile(':WAV:\w+\?', re.IGNORECASE)
    global rst_stats
    global cls_status

    if waveform_com.match(cmd):
        print(f'{cmd} is the command ')
        com, parameter = cmd.split(None, 1)
        type = com.split(':')[2]
        if type.upper() == 'SOUR':
            error = Chan.run(parameter, protocol) # Running 'run' function of the object while also logging any error that is returned
            if error is not None:
                print(error)  # If state temporarily went to error state, print the returned message
                return error
            print(f'{Chan.get_state()} is the current channel selected')
        elif type.upper() == 'MODE':
            error = Mode.run(parameter, protocol)
            if error is not None:
                print(error)  # If state temporarily went to error state, print the returned message
                return error
            print(f'{Mode.get_state()} is the current state of mode')
        elif type.upper() == 'FORM':
            error = Format.run(parameter, protocol)
            if error is not None:
                print(error)
                return error
            print(f'{Format.get_state()}')
        elif type.upper() == 'START':
            global wav_start
            status = Data_thread.set_start(parameter, Mode.get_state())
            if status is False:
                return f"Point out of range for mode {Mode.get_state()}"
            wav_start = int(parameter)
        elif type.upper() == 'STOP':
            global wav_stop
            status = Data_thread.set_stop(parameter, Mode.get_state())
            if status is False:
                return f"Point out of range for mode {Mode.get_state()}"
            wav_stop = int(parameter)
        else:
            print('#### Waveform command not found')
            return 'Waveform command not found'
    elif waveform_query.match(cmd):
        print(f'{cmd} is the query')
        type = cmd.split(':')[2]
        if type.upper() == 'SOUR?':
            print(Chan.get_state())
            return Chan.get_state()
        elif type.upper() == 'MODE?':
            print(Mode.get_state())
            return Mode.get_state()
        elif type.upper() == 'FORM?':
            print(Format.get_state())
            return Format.get_state()
        elif type.upper() == 'DATA?':
            global Wdata
            Wdata = D_Query.data_query()
            if rst_stats is not False and cls_status is not False:
                return "Data"
            else:
                return "Use the commands *CLS and *RST before returning data"
        elif type.upper() == 'START?':
            return Data_thread.get_start()
        elif type.upper() == 'STOP?':
            return Data_thread.get_stop()
        elif type.upper() == 'XINC?':
            return Data_thread.get_xinc(Chan.get_state(), Mode.get_state())
        elif type.upper() == 'XOR?':
            return Data_thread.get_xorg()
        elif type.upper() == 'XREF?':
            return Data_thread.get_xref()
        elif type.upper() == 'YINC?':
            return Data_thread.get_yinc()
        elif type.upper() == 'YOR?':
            return Data_thread.get_yorg()
        elif type.upper() == 'YREF?':
            return Data_thread.get_yref()
        elif type.upper() == 'PRE?':
            return preamble()
        else:
            print('waveform command not found')
            return "Waveform command not found, make sure you are using correct protocol 'S' or 'L'"

    elif cmd.upper() == ':RUN' or cmd.upper() == ':STOP':
        if cmd.upper() == ':RUN':
            if Mode.get_state() != 'RAW':
                Data_thread.set_wave_generation_state(True)
                Streamer.set_streaming_status(True)
            else:
                return "Turn off the RAW mode before running the sampler"
        else:
            Data_thread.set_wave_generation_state(False)
            Streamer.set_streaming_status(False)
        Sampling.run(cmd, protocol)
    elif cmd.upper() == '*RST':
        rst_stats = 1
        Mode.run('NORM', protocol)  # reset to default
        Chan.run('CHAN1', protocol)
        Format.run('BYTE', protocol)
        return "Everything has been set to default \n Mode: NORM \n Channel: CHAN1 \n Format: BYTE"
    elif cmd.upper() == '*CLS':
        cls_status = 1
        return "All Event Registers have been cleared"
    else:
        print('########################')
        print("Command not found, make sure you are sticking to the chosen protocol")
        return f"'{cmd}' Command not found, make sure you are sticking to the correct protocol (S or L)"

def preamble():
    format_ = f'<format> {Format.get_state()}\n'
    mode = f'<type> {Mode.get_state()}\n'
    points = ''
    if Mode.get_state() == 'NORM' or Mode.get_state() == 'MAX':
        points = f'<points> 120 for Normal/Max mode\n'
    else:
        points = f'<points> 1320 for Raw mode\n'
    xinc = f'<xincrement> {Data_thread.get_xinc(Chan.get_state(), Mode.get_state())}\n'
    xorg = f'<xorigin> {Data_thread.get_xorg()}\n'
    xref = f'<xreference> {Data_thread.get_xref()}\n'
    yinc = f'<yincrement> {Data_thread.get_yinc()}\n'
    yorg = f'<yorigin> {Data_thread.get_yorg()}\n'
    yref = f'<yreference> {Data_thread.get_yref()}\n'
    preamble_ = format_+mode+points+xinc+xorg+xref+yinc+yorg+yref
    return preamble_


if __name__ == "__main__":
    Sampling.add_state('Running', run_transition)
    Sampling.add_state('Stopped', run_transition)
    Chan.add_state('Chan1', channel_transition)
    Chan.add_state('Chan2', channel_transition)
    Chan.add_state('Chan3', channel_transition)
    Chan.add_state('Chan4', channel_transition)
    Chan.add_state('Math', channel_transition)
    Mode.add_state('Norm', mode_transition)
    Mode.add_state('Max', mode_transition)
    Mode.add_state('Raw', mode_transition)
    Format.add_state('Word', format_transition)
    Format.add_state('Byte', format_transition)
    Format.add_state('Ascii', format_transition)



    # setting the default state
    Sampling.set_start('Running')
    Chan.set_start('Chan1')
    Mode.set_start('Norm')
    Format.set_start('Byte')


    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) # this takes in three parameters, the read-list (the sockets you wanna read-in), write-list (sockets we wanna write to), and the sockets that we might error on
        #logging.debug("hello")
        #logging.debug(f'{Data_thread.get_wave_generation_state()} is the sampling rate \n {Data_thread.wave1} is wave')
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()

                user = receive_message(client_socket)
                if user is False:
                    continue

                protocol = receive_message(client_socket)

                sockets_list.append(client_socket)

                clients[client_socket] = user
                client_protocol[client_socket] = protocol

                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')} with preference of {protocol['data'].decode('utf-8')}")


            else:
                message = receive_message(notified_socket)

                if message == False:
                    print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                    sockets_list.remove(client_socket)
                    del clients[notified_socket]
                    continue

                user = clients[notified_socket]
                Query = commands(message['data'], client_protocol[notified_socket]) # if the message is a query, then store the returned value
                print(f"Received message from {user['data'].decode('utf-8')}| Message: {message['data'].decode('utf-8')}")

                if Query is not None:
                    if Query == 'Data':
                        #data_string = pickle.dumps(Wdata, -1)
                        data_string = (str(Wdata).encode("utf-8"))[1:-1]
                        #logging.critical(f' DAta string: {data_string}')
                        Data_Header = f"{len(data_string):<{HEADERSIZE}}".encode("utf-8")
                        notified_socket.send(Data_Header+data_string)
                    else:
                        Query = Query.encode('utf-8')
                        Query_header = f"{len(Query):<{HEADERSIZE}}".encode("utf-8")
                        #print(f'{Query} ids q {Query_header} is head')
                        notified_socket.send(Query_header+Query)
                else:
                    success = "Success".encode('utf-8')
                    success_header = f"{len(success):<{HEADERSIZE}}".encode('utf-8')
                    notified_socket.send(success_header+success)

                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(user['Header']+user['data']+message['Header']+message['data'])


                for notified_socket in exception_sockets:
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]


def preamble():
    format_ = f'<format> {Format.get_state()}\n'
    mode = f'<type> {Mode.get_state()}\n'
    points = ''
    if Mode.get_state() == 'NORM' or Mode.get_state() == 'MAX':
        points = f'<points> 120 for Normal/Max mode\n'
    else:
        points = f'<points> 1320 for Raw mode\n'
    xinc = f'<xincrement> {Data_thread.get_xinc(Chan.get_state(), Mode.get_state())}\n'
    xorg = f'<xorigin> {Data_thread.get_xorg()}\n'
    xref = f'<xreference> {Data_thread.get_xref()}\n'
    yinc = f'<yincrement> {Data_thread.get_yinc()}\n'
    yorg = f'<yorigin> {Data_thread.get_yorg()}\n'
    yref = f'<yreference> {Data_thread.get_yref()}\n'
    preamble_ = format_+mode+points+xinc+xorg+xref+yinc+yorg+yref
    return preamble_