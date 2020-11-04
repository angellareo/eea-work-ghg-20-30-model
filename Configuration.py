import numpy as np
import yaml

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Configuration(metaclass=Singleton):
        #@todo: move to yaml??
        firstYear = 2020
        lastYear = 2030
        years = np.arange(lastYear-firstYear+1) + firstYear
        nYears = len(years)

        def __init__(self, filename = "config.yaml"):
            pass
            # with open(filename,"r") as YAMLFile:
            #     configData = yaml.safe_load(YAMLFile)
            # self.runName = configData["runName"]
            # self.sectorIDs = configData["sectorIDs"]
            # self.nsectors = len(self.sectorIDs)
            # self.e0 = np.array(configData["e0"])
            # self.t0 = np.array(configData["t0"])
            # self.et0 = self.e0/self.t0
            # self.__parseScenarios(configData["Scenarios"])

        # def __parseScenarios(self, configScenarios):
        #     self.scenariosData = configScenarios