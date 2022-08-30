import json
from random import seed, choice
from math import ceil
import threading
import time

#import logging

class ElapsedTime():
    def __init__(self):
        self.start = time.time()

    def reset_start(self):
        self.start = time.time()

    def __call__(self):
        return int(time.time() - self.start)*1000000

class Wave_Data(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self):
        thread = threading.Thread(name="Wave_Data",target=self.run, args=())
        thread.daemon = True                            # Daemonize thread

        self.wave1 = {}
        self.voltage1 = []
        self.wave_iterator = 0
        self.file_number = 1
        self.play = True
        self.npoints = 120   # points of data stored in the array

        self.start = 120    # The last point is the start point
        self.stop = 0      # The first point is the stop

        thread.start()


    def generate_Wave(self):
        voltage_range = [50, 0] # keeping the range of teh square wave fixed for now
        if self.wave_iterator <= self.npoints and self.play is True:
            self.voltage1.append(choice(voltage_range))
            self.wave1[self.wave_iterator] = self.voltage1[self.wave_iterator]
            if self.wave_iterator >= self.npoints:
                self.wave_iterator = 0      # Hold 100 points of wave data in the immediate memory
                with open('data/data' + str(self.file_number) + '.json', 'w') as outfile:
                    json.dump(self.wave1, outfile, indent=1)
                    self.file_number = self.file_number + 1
                if(self.file_number == 11):
                    self.file_number = 1      # Total wave_data collection capacity is 10x500 points external memory
            self.wave_iterator = self.wave_iterator + 1

    def get_wave_data(self, channel=1):
        if channel == 1:
            values = list(self.wave1.values())
            return values
        elif channel == 2:
            pass

    def get_wave_data_norm(self, channel=1):
        if channel == 1:
            values = list(self.wave1.values())
            if self.stop > self.start:
                temp = self.stop
                self.stop = self.start
                self.start = temp
            try:
                return values[self.stop:self.start]
            except:
                return values[self.stop:self.wave_iterator] # if all 120 points have not been initialized
        elif channel == 2:
            pass

    def get_wave_data_raw(self, channel=1):
        temp_list = []
        values = list(self.wave1.values())
        if self.stop < self.start:      # This is opposite of what we did before since we are going back in memory
            temp = self.stop           # so max-start would be the last value in the array
            self.stop = self.start     # but 120 would be read as 1
            self.start = temp
        #temp_start = self.start
        if self.start < 120:
            temp_start = 120 - self.start
            temp_list = values[0:temp_start]

        no_of_files = ceil((self.stop - 120)/120)
        #logging.critical(f"THe no of files to be listed is {no_of_files}")
        for i in range(1, no_of_files):
            with open(f'data/data{i}.json', 'r') as f:
                voltage_dict = json.load(f)
                voltage_values = list(voltage_dict.values())
                if i == no_of_files:
                    temp_list.extend(voltage_values[0:self.stop-(120*(no_of_files-1))-1])
                else:
                    temp_list.extend(voltage_values)
        return temp_list

    def set_wave_generation_state(self, state=True):
        self.play = state

    def get_wave_generation_state(self):
        return self.play

    def set_npoints(self, num):
        self.npoints = num

    def get_start(self):
        return str(self.start)

    def get_stop(self):
        return str(self.stop)

    def get_yinc(self):
        return str((50/8)/25)+"e-03"    # hardcoded for now, 50mV / 8 grid lines

    def get_xinc(self, chan, mode):
        if mode == 'NORM' or mode == 'MAX':
            if chan != 'MATH':
                return str(0.1/100)+'e-06 s'  # Timescale/100 microseconds
            else:
                return str(0.1/100)+'e-06 Hz'
        elif mode == 'RAW':
            if chan != 'MATH':
                return str(0.1/100)+'e-06 s'  # Timescale/100 microseconds
            else:
                return str(0.1/100)+'e-06 Hz'

    def get_xorg(self):
        return "6.000000e-06  (dummy response)"

    def get_xref(self):
        return '0'

    def get_yorg(self):
        return '0'

    def get_yref(self):
        return '127'

    def set_start(self, parameter, mode):
        parameter = int(parameter)
        if mode == 'NORM':
            if 120 >= parameter >= 1:
                self.start = parameter
                return True
            else:
                return False
        elif mode == 'RAW':
            if 1319 >= parameter >= 1:        # 1320 - 1 = 120 (array size) x 10 (files)  +  120 (array variable) - 1
                self.start = parameter
                return True
            else:
                return False

    def set_stop(self, parameter, mode):
        parameter = int(parameter)
        if mode == 'NORM':
            if 120 >= parameter >= 1:
                self.stop = parameter
                return True
            else:
                return False
        elif mode == 'RAW':
            if 1319 >= parameter >= 1:        # 1320 - 1 = 120 (array size) x 10 (files)  +  120 (array variable) - 1
                self.stop = parameter
                return True
            else:
                return False

    def run(self):
        time1 = ElapsedTime()
        while True:
            time_period = time1()
            if time_period > 100000:    # basically every 0.1 micro seconds
                self.generate_Wave()
                time1.reset_start()


