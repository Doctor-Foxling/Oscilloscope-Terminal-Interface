import socket
import time
import sys
import errno
from GUI.Chat_Interface import *
from data.Client_display_wave import *
from data.data_streaming import DataReceiver
#import logging

#from Thread_frame_client import ClientThread

HEADERSIZE = 10

IP = "127.0.0.1"
PORT = 1234
STREAM_PORT = 4646

#logging.basicConfig(filename="Logs/client_log.log", level=logging.DEBUG)

####
tk_gui = GUI_Thread()
stream_receiver = DataReceiver(IP, STREAM_PORT)
wave_display = WaveDisplay()
my_username = None
protocol = None
client_socket = None

init_user = None        # Used to determine if the user has been registered in the GUI thread


def cl_exit():
    sys.exit()

while init_user == None:
    if tk_gui.exit_state is True:
        sys.exit()
    init_user = get_initialized()
    #my_username = input("Username: ")
    my_username = get_username()
    protocol_form_check = False
    protocol_form = ''
    while protocol_form_check is False:
        #protocol_form = input("Choose whether to use SHORT (S) or LONG (L) command form: ")
        if tk_gui.exit_state is True:
            sys.exit()
        protocol_form = get_protocol()
        try:
            if((protocol_form >= 'a') and (protocol_form <= 'z')) or ((protocol_form >='A') and (protocol_form <= 'Z')):
                if protocol_form == 's' or protocol_form == 'S' or protocol_form == 'L' or protocol_form == 'l':
                    protocol_form_check = True
                    protocol_error('NOERROR')
                    print("\n")
                    continue
            elif protocol is '':
                print("Wrong input: Tty 'S' or 'L' /n")
        except:
            continue

client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADERSIZE}}".encode("utf-8")
client_socket.send(username_header + username)

pro_Form = protocol_form.encode("utf-8")
pro_Form_Header = f"{len(pro_Form):<{HEADERSIZE}}".encode("utf-8")
client_socket.send(pro_Form_Header + pro_Form)

udp_iter = 0
udp_iter_temp = None


while True:
    #message = input(f"{my_username} > ")
    streamed_data = stream_receiver.get_received_data()
    if tk_gui.exit_state is True:
        sys.exit()

    # ------- Handling streamed data (skip this section (if loop below) to get to tcp based scpi message handling) --------------------

    if streamed_data:
        #logging.debug(f'The recived data is {streamed_data}')
        if streamed_data[1] == ':':
            udp_iter = streamed_data[0]
            #logging.debug(f'UDP ITER1 {udp_iter} and {streamed_data}')
        elif streamed_data[2] == ':':
            udp_iter = streamed_data[0] + streamed_data[1]
            #logging.debug(f'UDP ITER2 {udp_iter} and {streamed_data}')
        elif streamed_data[3] == ':':
            udp_iter = streamed_data[0] + streamed_data[1] + streamed_data[2]
            #logging.debug(f'UDP ITER3 {udp_iter}')
        elif streamed_data == 'Stopped':
            wave_display.set_running_state(False)
            #logging.critical("Got to stage 2")
        elif streamed_data == 'Running':
            wave_display.set_running_state(True)
            #logging.critical("Got to stage 2")

        if udp_iter != udp_iter_temp and udp_iter != 0:         # udp_iter != 0 is to check if the streaming has begun
            voltage = streamed_data[len(udp_iter)+1: len(streamed_data)]
            #logging.debug(f'UDP ITER HAHAH {voltage}')
            udp_iter_temp = udp_iter
            wave_display.set_voltage(int(voltage))


    # ---------- End of streamed data handling ------------------

    message = input_command()  # Gets the command entered by the user in the GUI (for the tcp socket)
    ques_mark = None
    com_opt = None
    Waveform_command = ''
    try:                                    #check if the function is a query
        message_txt = message  # check for other kinds of commands where there is no need to look for a pattern
        sep_message = message.split(':')
        com_opt = sep_message[2]
        Type = []
        #logging.info(f'Type before {Type} and com_opt is {com_opt}')
        Type[:0] = sep_message[2]   #[sep_message.length-1]  breaks sep_message[2] into individual characters in a list
        #logging.info(f'type[:0] is {Type[:0]} and Type is {Type}')
        Waveform_command = sep_message[1]       # check for :wav command
        print(Waveform_command)
        ques_mark = Type[len(Type) - 1]         # check for a query
    except:
        pass

    if message:
        message = message.encode("utf-8")
        message_header= f"{len(message):<{HEADERSIZE}}".encode("utf-8")

        client_socket.setblocking(True)
        client_socket.send(message_header + message)
        try:
            if ques_mark == '?':        # Recieve the incomming message immediately instead of waiting for the program to enter the recieving section
                time.sleep(0.2)
                if com_opt.upper() == 'DATA?':
                    message_header = client_socket.recv(HEADERSIZE)
                    message_length = int(message_header.decode("utf-8"))
                    client_socket.setblocking(False)
                    message_2 = b''

                    while len(message_2) < message_length:
                        #logging.error(f"len(message_2) is {len(message_2)} and message_length {message_length}")
                        more = client_socket.recv(600)   # receive data in chunks of 600 bytes
                        if not more:
                            raise EOFError('was expecting %d bytes but only received'
                                           ' %d bytes before the socket closed'
                                           % (message_length, len(message_2)))
                        message_2 += more

                    message_2_header = f"#9{'0'*(9-len(str(message_length)))}{message_length}"
                    message_2 = message_2.decode("utf-8")

                    insert_reply(message_2_header+" "+message_2)
                else:
                    client_socket.setblocking(False)
                    message_header = client_socket.recv(HEADERSIZE)
                    message_length = int(message_header.decode("utf-8"))
                    message_2=client_socket.recv(message_length).decode('utf-8')
                    print(message_2)
                    insert_reply(message_2) # passing the reply to the gui thread
            elif Waveform_command.upper() == 'WAV' or Waveform_command.upper() == 'WAVEFORM' or message_txt.upper() == ':RUN' or message_txt.upper() == ':STOP':
                time.sleep(0.2)
                client_socket.setblocking(False)
                message_header = client_socket.recv(HEADERSIZE)
                message_length = int(message_header.decode("utf-8"))
                message_2=client_socket.recv(message_length).decode('utf-8')
                if message_2=="Success":
                    opts = ''
                    try:
                        opts = com_opt.split(' ')
                        if opts[0].upper() == 'SOUR' or opts[0].upper() == 'SOURCE':
                            wave_display.display_selection(opts[1].upper())
                        elif opts[0].upper() == 'MODE':
                            wave_display.display_mode_selection(opts[1].upper())
                    except:
                        pass
                    print("Success")
                    insert_reply(message_2)
                else:
                    print("------------------------------------------------")
                    print(message_2)
                    insert_reply(message_2)  # passing the reply to the GUI thread
                    print("------------------------------------------------")

                if message_txt.upper() == ':RUN':
                    stream_receiver.set_receiving_status(True)
                    #logging.critical("Got to stage 1")
                elif message_txt.upper() == ':STOP':
                    stream_receiver.set_receiving_status(False)
                    #logging.critical("Got to stage 1")
            elif message_txt.upper() == '*CLS' or message_txt.upper() == '*RST':
                time.sleep(0.2)
                client_socket.setblocking(False)
                message_header = client_socket.recv(HEADERSIZE)
                message_length = int(message_header.decode("utf-8"))
                message_2 = client_socket.recv(message_length).decode('utf-8')
                insert_reply(message_2)
            else:
                client_socket.setblocking(False)
                insert_reply("Command not recognized, use the correct protocol")
                print("Command not recognized, use the correct protocol")
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                insert_reply("Reading error"+str(e))
                print("Reading error", str(e))

        except Exception as e:
            insert_reply('General Error'+str(e))
            print('General Error', str(e))


    try:
        while True:
            username_header = client_socket.recv(HEADERSIZE)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()
            username_length = int(username_header.decode("utf-8"))
            username = client_socket.recv(username_length).decode("utf-8")

            message_header = client_socket.recv(HEADERSIZE)
            message_length = int(message_header.decode("utf-8"))
            message = client_socket.recv(message_length).decode("utf-8")

            print('\n')
            print(f"{username} > {message}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("Reading error", str(e))
            sys.exit()
        continue

    except Exception as e:
        print('General Error', str(e))
        sys.exit()




