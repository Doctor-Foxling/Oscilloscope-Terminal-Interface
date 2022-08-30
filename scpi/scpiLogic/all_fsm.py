from scpi.stateMachine import StateMachine

Sampling = StateMachine()
Mode = StateMachine()
Chan = StateMachine()
Format = StateMachine()


def run_transition(command,protocol):
    if command.upper() == ":RUN":
        if Mode.get_state() == 'RAW':
            newState = "errorMessage - Can't run, Mode is set to 'RAW'"
        else:
            newState = "Running"
    elif command.upper() == ":STOP":
        newState = "Stopped"
    else:
        newState = "error_state"
    return newState

def channel_transition(command, protocol):
    if protocol == 'L':
        if command.upper() == 'CHANNEL1':
            newState = 'Chan1'
        elif command.upper() == 'CHANNEL2':
            newState = 'Chan2'
        elif command.upper() == 'CHANNEL3':
            newState = 'Chan3'
        elif command.upper() == 'CHANNEL4':
            newState = 'Chan4'
        elif command.upper() == 'MATH':
            if Mode.get_state() == 'RAW' or Mode.get_state() == 'MAX':
                newState = "errorMessage - Can't select the MATH channel in the 'RAW' or 'MAX' mode"
            else:
                newState = 'Math'
        else:
            newState = 'errorState'
    else:
        if command.upper() == 'CHAN1':
            newState = 'Chan1'
        elif command.upper() == 'CHAN2':
            newState = 'Chan2'
        elif command.upper() == 'CHAN3':
            newState = 'Chan3'
        elif command.upper() == 'CHAN4':
            newState = 'Chan4'
        elif command.upper() == 'MATH':
            if Mode.get_state() == 'RAW' or Mode.get_state() == 'MAX':
                newState = "errorMessage - Can't select the  MATH channel in the 'RAW' or 'MAX' mode"
            else:
                newState = 'Math'
        else:
            newState = 'errorState'
    return newState

def mode_transition(command, protocol):
    if protocol == 'L':
        if command.upper() == 'NORMAL':
            newState = "Norm"
        elif command.upper() == "MAXIMUM":
            if Chan.get_state() == 'MATH':
                #newState = Mode.get_state()  # Remain set to what it was before
                newState = "errorMessage - Only 'Normal' Mode can be selected when the 'Math' Channel is selected"
                print('###################')
                print(" --- Only 'Normal' Mode can be selected when the 'Math' Channel is selected")
            else:
                newState = "Max"
        elif command.upper() == "RAW":
            if Sampling.get_state() == 'RUNNING':
                #newState = Mode.get_state()
                newState = "errorMessage - Sampling needs to be turned off when setting the Mode to 'Raw' "
                print('####################')
                print(" --- Sampling needs to be turned off when setting the Mode to 'Raw' --- \n")
            elif Chan.get_state() == 'MATH':
                newState = "errorMessage - Only 'Normal' Mode can be selected when the 'Math' Channel is selected"
            else:
                newState = 'Raw'
        else:
            newState = "errorState"
        return newState
    else:
        if command.upper() == 'NORM':
            newState = "Norm"
        elif command.upper() == "MAX":
            if Chan.get_state() == 'MATH':
                #newState = Mode.get_state()  # Remain set to what it was before
                newState = "errorMessage - Only 'Normal' Mode can be selected when the 'Math' Channel is selected"
                print('###################')
                print(" --- Only 'Normal' Mode can be selected when the 'Math' Channel is selected")
            else:
                newState = "Max"
        elif command.upper() == "RAW":
            if Sampling.get_state() == 'RUNNING':
                #newState = Mode.get_state()
                newState = "errorMessage - Sampling needs to be turned off when setting the Mode to 'Raw' "
                print('####################')
                print(" --- Sampling needs to be turned off when setting the Mode to 'Raw' --- \n")
            elif Chan.get_state() == 'MATH':
                newState = "errorMessage - Only 'Normal' Mode can be selected when the 'Math' Channel is selected"
            else:
                newState = 'Raw'
        else:
            newState = "errorState"
        return newState

def format_transition(command, protocol):
    if protocol == 'L':
        if command.upper() == 'WORD':
            newState = 'Word'
        elif command.upper() == 'BYTE':
            newState = 'Byte'
        elif command.upper() == 'ASCII':
            newState = 'Ascii'
        else:
            newState = 'errorState'
        return newState
    if protocol == 'S':
        if command.upper() == 'WORD':
            newState = 'Word'
        elif command.upper() == 'BYTE':
            newState = 'Byte'
        elif command.upper() == 'ASC':
            newState = 'Ascii'
        else:
            newState = 'errorState'
        return newState
