import datetime
import inspect
import os


class Logging:
    ''' logs events in the folder of the caller location in the file <caller-name>.log

    Attributes
    ----------
    name : str
        base name of the log file
    console : bool
        whether display log events in stdout as well
    logpath : str
        complete path for the log file

    Methods
    ------------
    append(text='')
        append text to the logfile

    '''


    def __init__(self, name='', console=True):
        self.name = name
        self.console = console
        stack = inspect.stack()
        stacknum = 1 if len(stack) > 1 else 0
        previous = stack[stacknum].filename
        (callerdir, callername) = os.path.split(previous)
        if not self.name:
            self.name = os.path.splitext(callername)[0]
        logname = self.name + '.log'
        dirname = os.path.realpath(callerdir)
        self.logpath = os.path.join(dirname, logname)

    def append(self, text=''):
        if self.console:
            print(self.name + ": " + text)
        with open(self.logpath, 'a') as logfile:
            logfile.write(str(datetime.datetime.now()).split('.')[0] + " " + text + '\r\n')
