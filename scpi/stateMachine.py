
class InitializationError(Exception):

    def __init__(self, message):
        self.message = message

class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.currentState = None

    def add_state(self, name, handler):
        name = name.upper()
        self.handlers[name] = handler


    def set_start(self, name):
        self.startState = name.upper()
        self.currentState = self.startState

    def get_state(self):
        return self.currentState

    def get_default(self):
        return self.startState

    def run(self, cargo, protocol='L'):
        try:
            handler = self.handlers[self.currentState]
        except:
            raise InitializationError("must call .set_start() before .run()")

        newState = handler(cargo, protocol)
        if newState == 'errorState':
            self.currentState = self.startState
            return f"--- Command not found: Resetting to default - {self.startState} ---"
        elif newState[:12] == 'errorMessage':
            return newState[14:]

        self.currentState = newState.upper()
