# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#     Copyright 2019 Erich Kohmann                                              #
#                                                                               #
#     This file is part of IASIC.                                               #
#                                                                               #
#     IASIC is free software: you can redistribute it and/or modify             #
#     it under the terms of the GNU General Public License as published by      #
#     the Free Software Foundation, either version 3 of the License, or         #
#     (at your option) any later version.                                       #
#                                                                               #
#     IASIC is distributed in the hope that it will be useful,                  #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#     GNU General Public License for more details.                              #
#                                                                               #
#     You should have received a copy of the GNU General Public License         #
#     along with IASIC.  If not, see <https://www.gnu.org/licenses/>.          #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Package:      IASIC
# File:         classes/LogHandler.py
# Author:       Erich Kohmann (erich.kohmann@gmail.com)
# Description:  Used instead of `logging` to store and eventually print execution messages


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
