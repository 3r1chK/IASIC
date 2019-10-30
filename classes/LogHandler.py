import datetime


class LogHandler:

    logLevel = 3    # 0 - Errors; 1 - Warnings; 2 - Notices; 3 - Verbose

    def __init__(self, logging_level):
        self.logLevel = logging_level
        self.logPath = "./log"

    def write(self, msg, lvl=3):
        if lvl <= self.logLevel:
            prefix = "["+str(datetime.datetime.now())+"] "
            with open(self.logPath, "a") as f:
                f.write(prefix+msg+"\n")
                f.close()

    def print(self, msg, lvl):
        print(msg)
        self.write(msg, lvl)

    def __del__(self):
        self.logFile.close()
