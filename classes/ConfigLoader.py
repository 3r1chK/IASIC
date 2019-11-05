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
# File:         classes/ConfigLoader.py
# Author:       Erich Kohmann (erich.kohmann@gmail.com)
# Description:  Used to load sampling configurations


class ConfigLoader:

    configFileContent = []
    samplingConfiguration = []

    def __init__(self):
        self.data = []
        self.readFile()
        self.parseConfig()

    def readFile(self):
        rd = open("./config/config.txt", "r")
        self.configFileContent = rd.readlines()
        rd.close()
        return

    def parseConfig(self):
        for i in range(len(self.configFileContent)):
            self.configFileContent[i] = self.configFileContent[i].split(" ")
            if len(self.configFileContent[i]) != 2:
                self.configFileContent[i] = "Error"
            else:
                # Remove the new-line "\n" chars
                self.configFileContent[i][1] = self.configFileContent[i][1][:-1]
        result = []
        for conf in self.configFileContent:
            if len(conf) == 2:
                result.append(conf)
        self.samplingConfiguration = result
        self.configFileContent = []
        return
