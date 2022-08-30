import threading
import time
#from tkinter import *
from tkinter import ttk, Tk, END, FIRST, Button, Entry,Text,StringVar,Menu
from tkinter.font import Font
#import logging
import sys


send_dt = '' # Global variable for the client to access the commands typed into the GUI thread
reply = ''  #Global variable for the GUI get back the reply from server passed to the client prog
username = ''  #Global variable for the client prog to access the username from GUI
protocol = ''   #Global variable for the client prog to access the protocol from the GUI
initialized_user = None #Global variable for client prog to decide if the user is initialized in the GUI
protocol_err = ''   #Global variable for client to know if wrong input is given to the protocol entry
skip_empty = 0
exit_state = False
menu_used = False
menu_reply = ''
looks = 'Default'
wav_start = 12000  #by default out of range to counter any problems
wav_stop = 12000

#--------- Not so important stuff -----
popup = 0
welcome = 0
# -----------------------------------

NORM_FONT= ("Verdana", 10)

class GUI_Thread(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

        self.exit_state = False

    def client_exit(self):
        self.exit_state = True

    def popupmsg(self):
        popup = Tk()
        popup.after(1, lambda: popup.focus_force())
        popup.wm_title("register")
        label = ttk.Label(popup, text='Enter Details', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        label = ttk.Label(popup, text='Username: ', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=2)
        username_entry = Entry(popup, width=30)
        username_entry.pack(pady = 5, padx = 15)
        username_entry.focus()
        #print(f'form thread {username}')
        label = ttk.Label(popup, text='Enter Protocol', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=2)
        protocol_entry = Entry(popup, width =30)
        protocol_entry.pack(pady=5, padx=15)
        def destroy_pop(*args):   # *args is passed as the parameters because binding to a key expects some
            global username
            global protocol
            error_var = StringVar()
            username = username_entry.get()
            protocol = protocol_entry.get()
            error_msg = ttk.Label(popup, text="Enter S or L as the protocol")
            error_msg.pack(side="bottom", fill="x", pady=10)
            error_msg.pack_forget()
            #error_msg.pack()
            if protocol_err != 'NOERROR':
                error_msg.pack()
                #error_var.set("Enter S or L as the protocol")
            else:
                error_msg.pack_forget()
                popup.destroy()
        protocol_entry.bind("<Return>",destroy_pop)
        B1 = ttk.Button(popup, text="Register", command=destroy_pop)
        B1.pack()
        popup.mainloop()

    def data_start_pos(self):
        popup = Tk()
        popup.after(1, lambda: popup.focus_force())
        popup.wm_title("Set Data Positions")
        label = ttk.Label(popup, text='Enter Start position', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        label = ttk.Label(popup, text='Wave Start: ', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=2)
        start_entry = Entry(popup, width=30)
        start_entry.pack(pady=5, padx=15)
        start_entry.focus()
        def destroy_pop(*args):   # *args is passed as the parameters because binding to a key expects some
            global wav_start
            wav_start = start_entry.get()
            set_start()
            popup.destroy()
        start_entry.bind("<Return>",destroy_pop)
        B1 = ttk.Button(popup, text="Set Value", command=destroy_pop)
        B1.pack()
        popup.mainloop()

    def data_stop_pos(self):
        popup = Tk()
        popup.after(1, lambda: popup.focus_force())
        popup.wm_title("Set Stop Data Position")
        label = ttk.Label(popup, text='Enter Stop position', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        label = ttk.Label(popup, text='Wave Stop', font=NORM_FONT)
        label.pack(side="top", fill="x", pady=2)
        stop_entry = Entry(popup, width=30)
        stop_entry.pack(pady=5, padx=15)
        stop_entry.focus()
        def destroy_pop(*args):   # *args is passed as the parameters because binding to a key expects some
            global wav_stop
            wav_stop = stop_entry.get()
            set_stop()
            popup.destroy()
        stop_entry.bind("<Return>",destroy_pop)
        B1 = ttk.Button(popup, text="Set Value", command=destroy_pop)
        B1.pack()
        popup.mainloop()

    def run(self):
        root = Tk()

        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff=1)
        editmenu = Menu(menubar, tearoff=0)
        querymenu = Menu(menubar, tearoff=0)
        channel = Menu(filemenu, tearoff=0)
        mode = Menu(filemenu, tearoff=0)
        format_ = Menu(filemenu, tearoff=0)
        appearance = Menu(editmenu, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label='Query', menu=querymenu)
        menubar.add_command(label="Quit", command=self.client_exit)

        filemenu.add_command(label='Run', command=select_run)
        filemenu.add_command(label='Stop', command=select_stop)
        filemenu.add_separator()

        filemenu.add_cascade(label='Select Channel', menu=channel)
        channel.add_command(label='Channel 1', command=select_channel1)
        channel.add_command(label='Channel 2', command=select_channel2)
        channel.add_command(label='Channel 3', command=select_channel3)
        channel.add_command(label='Channel 4', command=select_channel4)
        channel.add_command(label='Math Channel', command=select_math)

        filemenu.add_cascade(label='Select Mode', menu=mode)
        mode.add_command(label='Normal',command=select_Norm)
        mode.add_command(label='Raw', command=select_Raw)
        mode.add_command(label='Maximum', command=select_Max)

        filemenu.add_cascade(label='Select Format', menu=format_)
        format_.add_command(label='Byte', command=select_byte)
        format_.add_command(label='Ascii', command=select_asc)
        format_.add_command(label='Word', command=select_word)

        filemenu.add_separator()
        filemenu.add_command(label='*CLS', command=select_cls)
        filemenu.add_command(label='*RST', command=select_rst)
        filemenu.add_separator()
        filemenu.add_command(label='Set Wave-Start', command=self.data_start_pos)
        filemenu.add_command(label="Set Wave-Stop", command=self.data_stop_pos)

        editmenu.add_cascade(label='Appearance',menu=appearance)
        appearance.add_command(label='Default', command=default_appearance)
        appearance.add_command(label='Dracula', command=dracula_appearance)

        querymenu.add_command(label='Channel',command=query_source)
        querymenu.add_command(label='Mode',command=query_mode)
        querymenu.add_command(label='Format',command=query_format)
        querymenu.add_command(label='Data',command=query_data)

        querymenu.add_separator()

        querymenu.add_command(label='Start',command=query_start)
        querymenu.add_command(label='Stop',command=query_stop)

        querymenu.add_separator()
        querymenu.add_command(label='X-Reference',command=query_xref)
        querymenu.add_command(label='X-Origin',command=query_xor)
        querymenu.add_command(label='X-Increment',command=query_xinc)
        querymenu.add_command(label='Y-Reference',command=query_yref)
        querymenu.add_command(label='Y-Origin',command=query_yor)
        querymenu.add_command(label='Y-Increment',command=query_yinc)

        querymenu.add_separator()
        querymenu.add_command(label='Preamble', command=preamble)

        root.config(menu=menubar)
        menubar.entryconfig("File", state="disabled")
        menubar.entryconfig("Edit", state="disabled")

        bold_font = Font(root=root.master,family="Helvetica", size=11, weight="bold")
        def send(*args):
            nonlocal root
            global send_dt
            global reply
            global username
            global initialized_user
            global skip_empty
            # if initialized_user == None:
            #     self.popupmsg()
            #     #initialized_user = 1       # This is done when the username is initialized

            def handle_usr_wlcm():
                global popup
                global welcome
                if initialized_user == None:
                    if username == '' and popup == 0:
                        self.popupmsg()
                        popup = 1
                        root.after(200,handle_usr_wlcm)
                    elif username == '' and popup == 1:
                        root.after(200,handle_usr_wlcm)
                elif welcome == 0:
                    txt.insert(END,"\nWelcome "+username+"\n\n","Blue")
                    menubar.entryconfig("File", state="normal")
                    menubar.entryconfig("Edit", state="normal")
                    welcome = 1
            handle_usr_wlcm()

            send_dt=e.get()
            send_dt_temp =send_dt
            e.delete(0, END)
            e.config(state='disabled') #Make sure pressing enter quickly doesn't the same command multiple commands to the server, resulting in multiple replies
            e.unbind("<Return>")
            if send_dt_temp == '':
                skip_empty = 1          # deal with situation: If enter is pressed with no value
            if looks == 'Default':
                txt.insert(END,"\n"+username+'> ',"BOLD_Red")
                txt.insert(END, send_dt_temp)
            elif looks == 'Dracula':
                txt.insert(END, "\n"+username+'> ',"usr_dark")
                txt.insert(END, send_dt_temp, "White")

            def callback():
                global reply
                global looks
                global skip_empty
                if reply == '' and skip_empty == 0:  #Don't get past this until you get a reply
                    root.after(500,callback)  # This is needed to make sure that even if we are stuck in a loop, tkinter still finishes its loop to display the GUI
                    e.config(state='disabled')
                else:
                    e.config(state='normal')
                    if looks == 'Default':
                        txt.insert(END, "\n" + reply, "\n")

                    elif looks == 'Dracula':
                        txt.insert(END, "\n" + reply+"\n","White")
                    txt.see("end")
                    reply = ''
                    e.bind("<Return>", send)
                    skip_empty = 0

            root.after(500,callback)
        reply = ''
        txt = Text(root)
        # ------ Add bunch of text options that could be used on the text ----------------
        txt.tag_configure('BOLD_Red', font=bold_font, foreground = 'red') # Add the option of 'Bold' for the text object
        txt.tag_configure('Red_1', foreground='red')
        txt.tag_configure('Blue', foreground='blue')
        txt.tag_configure('White', foreground='white')
        txt.tag_configure('Menu_Rep', foreground='yellow', background='#313632')
        txt.tag_configure('Menu_Rep2', foreground='#1a3d23', background='#dfe6e0')
        txt.tag_configure('usr_dark', font=bold_font, foreground='#6b97e8')
        #  ------------

        txt.grid(row=0,column=0, columnspan=3)


        def menu_check_callback():
            global menu_reply
            global looks
            #logging.info('Getting here')
            if menu_reply != '':
                txt.insert(END,"\n")
                if looks == 'Dracula':
                    txt.insert(END,menu_reply+"\n","Menu_Rep")
                elif looks == 'Default':
                    txt.insert(END,menu_reply+"\n","Menu_Rep2")
                #logging.debug(f'in the menu text option')
                menu_reply = ''
                txt.see("end")
            if looks == 'Default':
                txt.configure(background='white')
            elif looks == 'Dracula':
                txt.configure(background='#373b38')

            root.after(600, menu_check_callback)
        root.after(500,menu_check_callback)
        send_key = Button(root,text="Send", command=send).grid(row=1,column=1, padx=1, ipady=8, ipadx=15, pady=2)
        e=Entry(root,width=100)
        e.bind("<Return>",send)
        e.grid(row=1,column=0, padx=10)
        e.focus()

        w = 700  # width for the Tk root
        h = 435  # height for the Tk root

        # get screen width and height
        ws = root.winfo_screenwidth()  # width of the screen
        hs = root.winfo_screenheight()  # height of the screen
        root.geometry('%dx%d+%d+%d' % (w, h, 0, 0))

        root.title("Scpi_Gui")
        root.mainloop()



def input_command():    #To Transfer the commands entered in the GUI to the client program
    global send_dt
    if send_dt != '':
        temp = send_dt
        send_dt = ''
        return temp

def protocol_error(p_err):  #If the protocol typed into the GUI is incorrect, let the client program know there is an error so it can deal with the logic of it
    global protocol_err
    protocol_err = p_err


def insert_reply(client_reply): #Take the reply from the server to the client program so the GUI thread has access to it
    global reply
    global menu_used
    global menu_reply
    reply = client_reply
    if menu_used is True:
        menu_reply = client_reply
        #logging.debug(f'Heres menu reply: {menu_reply}')
        menu_used = False

def get_username(): #Get username typed into the GUI popup message for initialization
    global username
    global initialized_user
    if username != '':
        initialized_user = 1 # To make sure the username is not NONE when initialized_user is set to 1
        return username

def get_protocol(): #Get the username typed into the GUI popup message for the initialization
    global protocol
    if protocol != '':
        return protocol

def get_initialized():  # Tells the client program if the user has been initialized or not so the client and the server can use the username and the protocol
    global initialized_user
    if initialized_user != '':
        return initialized_user

def select_channel1():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:SOUR CHAN1'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:SOURCE CHANNEL1'
    menu_used = True


def select_channel2():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:SOUR CHAN2'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:SOURCE CHANNEL2'
    menu_used = True

def select_channel3():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:SOUR CHAN3'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:SOURCE CHANNEL3'
    menu_used = True

def select_channel4():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:SOUR CHAN4'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:SOURCE CHANNEL4'
    menu_used = True

def select_math():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:SOUR MATH'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:SOURCE MATH'
    menu_used = True


def select_Norm():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:Mode Norm'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:Mode Normal'
    menu_used = True


def select_Raw():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:MODE RAW'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:MODE RAW'
    menu_used = True


def select_Max():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:Mode Max'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:Mode Maximum'
    menu_used = True

def select_stop():
    global send_dt
    global menu_used
    send_dt = ':stop'
    menu_used = True

def select_run():
    global send_dt
    global menu_used
    send_dt = ':run'
    menu_used = True

def select_byte():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:form byte'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:FORMat Byte'
    menu_used = True

def select_asc():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:form asc'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:FORMat Ascii'
    menu_used = True

def select_word():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:form word'
    elif protocol.upper() == 'L':
        send_dt = ':WAVEFORM:FORMat Word'
    menu_used = True

def select_cls():
    global send_dt
    global menu_used
    send_dt = '*CLS'
    menu_used = True

def select_rst():
    global send_dt
    global menu_used
    send_dt = '*RST'
    menu_used = True

def query_source():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:sour?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:source?'
    menu_used = True

def query_mode():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:mode?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:mode?'
    menu_used = True

def query_format():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:form?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:format?'
    menu_used = True

def query_data():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:data?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:data?'
    menu_used = True

def query_start():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:start?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:start?'
    menu_used = True

def query_stop():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:stop?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:stop?'
    menu_used = True

def query_xinc():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:xinc?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:Xincrement?'
    menu_used = True

def query_yinc():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:yinc?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:yincrement?'
    menu_used = True

def query_xor():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:xor?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:Xorigin?'
    menu_used = True

def query_yor():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:yor?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:yorigin?'
    menu_used = True

def query_xref():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:xref?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:xreference?'
    menu_used = True

def query_yref():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:yref?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:yreference?'
    menu_used = True

def preamble():
    global send_dt
    global menu_used
    global protocol
    if protocol.upper() == 'S':
        send_dt = ':WAV:pre?'
    elif protocol.upper() == 'L':
        send_dt = ':WAveform:PReamble?'
    menu_used = True

def set_start():
    global send_dt
    global menu_used
    global wav_start
    global protocol
    if protocol.upper() == 'S':
        send_dt = f':WAV:start {wav_start}'
    elif protocol.upper() == 'L':
        send_dt = f':WAveform:start {wav_start}'
    wav_start = 12000 # something out of range
    menu_used = True

def set_stop():
    global send_dt
    global menu_used
    global wav_stop
    global protocol
    if protocol.upper() == 'S':
        send_dt = f':WAV:start {wav_stop}'
    elif protocol.upper() == 'L':
        send_dt = f':WAveform:start {wav_stop}'
    wav_stop = 12000 # something out of range
    menu_used = True

def default_appearance():
    global looks
    looks = 'Default'

def dracula_appearance():
    global looks
    looks = 'Dracula'