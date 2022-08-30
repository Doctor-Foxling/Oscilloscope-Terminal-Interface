import sys
import tkinter as tk
import threading
from random import randint, seed, choice
#import logging

seed(3)
i = 0


class App(tk.Frame):
    def __init__(self, parent, title):
        tk.Frame.__init__(self, parent)
        self.npoints = 400
        self.Line1 = [0 for x in range(self.npoints)]
        #self.Line2 = [0 for x in range(self.npoints)]
        #self.Line3 = [0 for x in range(self.npoints)]
        parent.wm_title(title)
        parent.wm_geometry("1000x400")
        self.canvas = tk.Canvas(self, background="white")
        self.canvas.bind("<Configure>", self.on_resize)

        # add grid
        widx = 800 / 50
        widy = 300 / 25
        for i in range(50):
            self.canvas.create_line(((widx * i) + 100, 50, (widx * i) + 100, 350), fill="#abc973")
        for i in range(25):
            self.canvas.create_line((100, widy * i + 50, 900, widy * i + 50), fill="#abc973")

        self.canvas.create_text(500, 20, font=("Purisa", 20), text="Server-Data Live Stream", fill="#3c66a3")

        self.canvas.create_line((0, 0, 0, 0), tag='X', fill='darkblue', width=1)
        #self.canvas.create_line((0, 0, 0, 0), tag='Y', fill='darkred', width=1)
        #self.canvas.create_line((0, 0, 0, 0), tag='Z', fill='darkgreen', width=1)
        self.canvas.create_rectangle(100, 50, 900, 350, outline="#d4b359", width=10)
        self.Stopped_txt = self.canvas.create_text((500, 200), font=("Purisa", 40), text="Stopped", fill="Red", state="hidden")

        self.canvas.grid(sticky="news")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky="news")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.sel_chan = self.canvas.create_text((75, 200), font=("Calibri", 10), text="- Chan1: ", fill="#199c33", state="normal")
        self.chan1 = self.canvas.create_text((200, 375), font=("Calibri", 15), text="- Chan1 selected -", fill="#199c33", state="normal")
        self.chan2 = self.canvas.create_text((200, 375), font=("Calibri", 15), text="- Chan2 selected -", fill="#ab1648", state="hidden")
        self.chan3 = self.canvas.create_text((200, 375), font=("Calibri", 15), text="- Chan3 selected -", fill="#511b96", state="hidden")
        self.chan4 = self.canvas.create_text((200, 375), font=("Calibri", 15), text="- Chan4 selected -", fill="#196685", state="hidden")
        self.math_chan = self.canvas.create_text((200, 375), font=("Calibri", 15), text="- Math Channel -", fill="#1ca6a5", state="hidden")

        self.mode_norm = self.canvas.create_text((400, 375), font=("Calibri", 15), text="- Mode: Normal -",fill="#19665a", state="normal")
        self.mode_raw = self.canvas.create_text((400, 375), font=("Calibri", 15), text="- Mode: Raw -", fill="#17665b", state="hidden")
        self.mode_max = self.canvas.create_text((400, 375), font=("Calibri", 15), text="- Mode: Maximum -", fill="#18665c", state="hidden")

        #self.wave = {}
        self.voltage = 0
        self.temp_voltage = 0
        self.tempx = 0
        self.running_state = True

    def on_resize(self, event):
        self.replot()

    def set_voltage(self, voltage):
        self.voltage = voltage
        #logging.info(f'from set voltage APP {self.voltage}')

    def set_running_state(self, state=True):
        #logging.info(f'from APP set running state state = {state} self.rn_state = {self.running_state}')
        self.running_state = state
        if state is False:
            self.canvas.itemconfigure(self.Stopped_txt, state='normal')
        elif state is True:
            self.canvas.itemconfigure(self.Stopped_txt, state='hidden')

    def process_data(self):
        global i
        if i < 1001:            # Just an infinite loop that is non blocking
            if (i == 1000):
                i = 0
            try:
                self.append_values(self.voltage)
                self.after_idle(self.replot)        # Call the replot function whenever the thread is idle
            except Exception as e:
                print(e)
            i = i + 1
            self.after(50, self.process_data)

    def append_values(self, x):
        """
        Update the cached data lists with new sensor values.
        """
        self.Line1.append(float(x))
        # print(f'Loking for this {self.Line1[-1 * self.npoints:]}')
        self.Line1 = self.Line1[-1 * self.npoints:]
        # self.Line2.append(float(y))
        # self.Line2 = self.Line2[-1 * self.npoints:]
        # self.Line3.append(float(z))
        # self.Line3 = self.Line3[-1 * self.npoints:]
        return

    def replot(self):
        """
        Update the canvas graph lines from the cached data lists.
        The lines are scaled to match the canvas size as the window may
        be resized by the user.
        """
        if self.running_state:
            w = self.winfo_width()
            h = self.winfo_height()
            max_X = max(self.Line1) + 1e-5
            #max_Y = max(self.Line2) + 1e-5
            #max_Z = max(self.Line3) + 1e-5
            max_all = 200.0
            coordsX, coordsY, coordsZ = [], [], []
            for n in range(48, self.npoints):
                x = ((w-100) * n / self.npoints)
                if self.temp_voltage != self.Line1[n]:
                    coordsX.append(self.tempx)
                    coordsX.append(h - ((h * (self.Line1[n] + 100)) / max_all))
                    coordsX.append(x)
                    coordsX.append(h - ((h * (self.Line1[n] + 100)) / max_all))
                    # coordsY.append(x)
                    # coordsY.append(h - ((h * (self.Line2[n]+100)) / max_all))
                    # coordsZ.append(x)
                    # coordsZ.append(h - ((h * (self.Line3[n] + 100)) / max_all))
                else:
                    coordsX.append(x)
                    coordsX.append(h - ((h * (self.temp_voltage + 100)) / max_all))
                self.temp_voltage = self.Line1[n]
                self.tempx = x
            # print(f'Hi {coordsX}')
            self.canvas.coords('X', *coordsX)
            self.canvas.coords('Y', *coordsY)
            self.canvas.coords('Z', *coordsZ)

    def display_selection(self, Chan):
        if Chan == 'CHAN1' or Chan == 'CHANNEL1':
            self.canvas.itemconfigure(self.chan1, state='normal')
            self.canvas.itemconfigure(self.chan2, state='hidden')
            self.canvas.itemconfigure(self.chan3, state='hidden')
            self.canvas.itemconfigure(self.chan4, state='hidden')
            self.canvas.itemconfigure(self.math_chan, state='hidden')
        elif Chan == 'CHAN2' or Chan == 'CHANNEL2':
            self.canvas.itemconfigure(self.chan1, state='hidden')
            self.canvas.itemconfigure(self.chan2, state='normal')
            self.canvas.itemconfigure(self.chan3, state='hidden')
            self.canvas.itemconfigure(self.chan4, state='hidden')
            self.canvas.itemconfigure(self.math_chan, state='hidden')
        elif Chan == 'CHAN3' or Chan == 'CHANNEL3':
            self.canvas.itemconfigure(self.chan1, state='hidden')
            self.canvas.itemconfigure(self.chan2, state='hidden')
            self.canvas.itemconfigure(self.chan3, state='normal')
            self.canvas.itemconfigure(self.chan4, state='hidden')
            self.canvas.itemconfigure(self.math_chan, state='hidden')
        elif Chan == 'CHAN4' or Chan == 'CHANNEL4':
            self.canvas.itemconfigure(self.chan1, state='hidden')
            self.canvas.itemconfigure(self.chan2, state='hidden')
            self.canvas.itemconfigure(self.chan3, state='hidden')
            self.canvas.itemconfigure(self.chan4, state='normal')
            self.canvas.itemconfigure(self.math_chan, state='hidden')
        elif Chan == 'MATH':
            self.canvas.itemconfigure(self.chan1, state='hidden')
            self.canvas.itemconfigure(self.chan2, state='hidden')
            self.canvas.itemconfigure(self.chan3, state='hidden')
            self.canvas.itemconfigure(self.chan4, state='hidden')
            self.canvas.itemconfigure(self.math_chan, state='normal')

    def display_mode_selection(self, Mode):
        if Mode == 'NORM' or Mode == 'NORMAL':
            self.canvas.itemconfigure(self.mode_norm, state='normal')
            self.canvas.itemconfigure(self.mode_raw, state='hidden')
            self.canvas.itemconfigure(self.mode_max, state='hidden')
        elif Mode == 'RAW':
            self.canvas.itemconfigure(self.mode_norm, state='hidden')
            self.canvas.itemconfigure(self.mode_raw, state='normal')
            self.canvas.itemconfigure(self.mode_max, state='hidden')
        elif Mode == 'MAX' or Mode == 'MAXIMUM':
            self.canvas.itemconfigure(self.mode_norm, state='hidden')
            self.canvas.itemconfigure(self.mode_raw, state='hidden')
            self.canvas.itemconfigure(self.mode_max, state='normal')


class WaveDisplay(object):
    def __init__(self):
        thread = threading.Thread(name="Wave_Display", target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

        self.app = None

    def set_voltage(self, voltage):
        #logging.warning(f'here i am {voltage}')
        if self.app != None:
            self.app.set_voltage(voltage)
            self.app.process_data()

    def set_running_state(self, state):
        if self.app is not None:
            self.app.set_running_state(state)
    # def check_volts(self, app):
    #     logging.info(f'Bugs bugs every wehre {app.npoints}')
    #     if self.volts != None:
    #         app.set_voltage(self.volts)
    #         try:
    #             logging.critical(f'file number {app.file_number}')
    #         except Exception as e:
    #             logging.critical(f'Exception occured {e}')
    #         app.process_data()
    #         self.volts = None

    def display_selection(self, Chan):
        if self.app is not None:
            self.app.display_selection(Chan)

    def display_mode_selection(self, Mode):
        if self.app is not None:
            self.app.display_mode_selection(Mode)

    def run(self):
        root = tk.Tk()
        w = 1000  # width for the Tk root
        h = 400  # height for the Tk root

        # get screen width and height
        ws = root.winfo_screenwidth()  # width of the screen
        hs = root.winfo_screenheight()  # height of the screen
        app = App(root, "Smooth Sailing")
        root.geometry('%dx%d+%d+%d' % (w, h, 550,400))
        self.app = app
        app.mainloop()
        return 0
