
class DataQuery():
    def __init__(self, Chan, Mode, Format, Sampling, Wave_Data):
        self.Chan = Chan
        self.Mode = Mode
        self.Format = Format
        self.Sampling = Sampling
        self.Wave_Data = Wave_Data


    def data_query(self):
        if self.Mode.get_state() == 'NORM':
            if self.Chan.get_state() == 'CHAN1':
                wave_values = self.Wave_Data.get_wave_data_norm(1)
                temp_list = []
                if self.Format.get_state() == 'ASCII':
                    return wave_values
                elif self.Format.get_state() == 'BYTE':
                    for i in range(0, len(wave_values)):
                        temp_list.append(bin(int(wave_values[i])))
                    return temp_list
                elif self.Format.get_state() == 'WORD':
                    for i in range(0, len(wave_values)):
                        bin_value = bin(int(wave_values[i]))
                        temp_list.append("00000000"+str(bin_value))
                    return temp_list
            elif self.Chan.get_state() == 'CHAN2':
                return " Not Connected - Data not available for CHAN2"
            elif self.Chan.get_state() == 'CHAN3':
                return " Not Connected - Data not available for CHAN3"
            elif self.Chan.get_state() == 'CHAN4':
                return " Not Connected - Data not available for CHAN4"
            elif self.Chan.get_state() == 'MATH':
                return " Not Connected - Data not available for MATH channel"
        elif self.Mode.get_state() == 'RAW':
            if self.Chan.get_state() == 'CHAN1':
                wave_values = self.Wave_Data.get_wave_data_raw(1)
                temp_list = []
                if self.Format.get_state() == 'ASCII':
                    return wave_values
                elif self.Format.get_state() == 'BYTE':
                    for i in range(0, len(wave_values)):
                        temp_list.append(bin(int(wave_values[i])))
                    return temp_list
                elif self.Format.get_state() == 'WORD':
                    for i in range(0, len(wave_values)):
                        bin_value = bin(int(wave_values[i]))
                        temp_list.append("00000000"+str(bin_value))
                    return temp_list
            elif self.Chan.get_state() == 'CHAN2':
                return " Not Connected - Data not available for CHAN2"
            elif self.Chan.get_state() == 'CHAN3':
                return " Not Connected - Data not available for CHAN3"
            elif self.Chan.get_state() == 'CHAN4':
                return " Not Connected - Data not available for CHAN4"

        elif self.Mode.get_state() == 'MAX':
            return " Old Version - MAX functionality yet to be implemented"
