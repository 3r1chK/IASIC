
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
