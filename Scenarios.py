import numpy as np

from Sectors import *

from Configuration import Configuration

class Scenario:
    def __init__(self, name, scenarioData):
        self.name = name
        self.ef = scenarioData['ef']
        if 'Sectors' in scenarioData:
            self.__createSectors(scenarioData["Sectors"])

    def __createSectors(self, sectorsData):
        cfg = Configuration()
        self.sectorsP = []
        self.sectorNames = []
        #@todo: comprobar que no se incumplen las restricciones de emisiones
        i = 0
        depentedSectors = []
        for sectorID in sectorsData:
            self.sectorNames.append(sectorID)
            if sectorID in sectorsData:
                if (sectorsData[sectorID]["type"] == "Dependent"):
                    depentedSectors.append(i)
                self.sectorsP.append(self.__newSector(sectorID, sectorsData[sectorID]))
            #else:
            #    self.sectorsP.append(self.__newNoneDataSector(self.ef[i], sectorID))
            i+=1
        for i in depentedSectors:
            assSectorsStr = sectorsData[self.sectorsP[i].name]['data']['assSector']
            assSectorsList = assSectorsStr.split('/')
            print(assSectorsList)
            for assSector in assSectorsList:
                assSectorN = self.sectorNames.index(assSector)
                self.sectorsP[i].assSectorObjs.append(self.sectorsP[assSectorN])

    # def __newNoneDataSector(self, ef, sectorID):
    #     cfg = Configuration()
    #     endYear=cfg.firstYear+cfg.nYears-1
    #     n = cfg.sectorIDs.index(sectorID)
    #     e0 = cfg.e0[n]
    #     t0 = cfg.t0[n]
    #     stdSData = {
    #         'type': "Interpolated",
    #         'indV': 'e',
    #         'maxIncr': 5,
    #         'maxDecr': 5,
    #         'data': {
    #             cfg.firstYear: eval(self.indV+"0"),
    #             endYear: eval("self."+self.indV+"f["+str(n)+"]") 
    #         }
    #     }
    #     return InterpolatedSector(ef, sectorID, stdSData)

    def __newSector(self, sectorID, sectorsData):
        return eval(Sector.STypes[sectorsData['type']]+"(sectorID, sectorsData)")

    # def __checkETFContraints(self):
    #     etf = self.ef/self.tf
    #     cfg = Configuration()
    #     for etfSector in self.etf:
    #         if ( etfSector<(cfg.et0-0.01) or etfSector>(cfg.et0+0.01)):
    #             raise Exception("ef/tf violates restriction in scenario " + self.name)

    # def step(self):
    #     for sector in sectorsP:
    #         sector.step()

    def getNSectors(self):
        return len(self.sectorsP)


