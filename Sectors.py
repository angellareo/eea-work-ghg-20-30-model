import numpy as np

from Configuration import Configuration
## Las matrices (TMat, EMat) almacenan los incrementos relativos al primer año

class Sector: 
    STypes = {   'Interpolated': "InterpolatedSector",
                'Predetermined': "PredeterminedSector",
                'Dependent': "DependentSector" }

    def __init__(self, sectorID, sectorData):
        self.name = sectorID
        self.indV = sectorData["indV"]
        self.constrained = [False for i in range(Configuration.nYears)]
        self.e0 = sectorData['e0']
        self.t0 = sectorData['t0']
        if self.t0==0:
            raise Exception (sectorID + ": Invalid t0 = 0.")
        self.eTConstant = self.e0/self.t0
        if self.indV=='t':
            self.tf = sectorData['mf']
        elif self.indV=='e':
            self.tf = sectorData['mf'] / self.eTConstant
        else:
            raise Exception ("Unrecognized indV in sector " + sectorID)
        self.currentStep = -1
        

    def __getitem__(self, year):
        return self.getRelYear(year)

    def getAbsYear(self, year):
        absE = self.e0 + self.e0*self.m[0];
        absT = self.t0 + self.t0*self.m[0];
        for i in range(year-Configuration.firstYear):
            absE = absE + absE*self.m[i+1]
            absT = absT + absT*self.m[i+1]
        return [absE, absT]

    def getRelYear(self, year):
        i=year-Configuration.firstYear
        return [self.m[i], self.m[i]]

    def getData(self, ini, fin):
        if (ini<Configuration.firstYear) or (ini>=Configuration.firstYear+Configuration.nYears):
            raise Exception("ini("+str(ini)+") must be between "+
                str(Configuration.firstYear) + " and " + str(Configuration.firstYear+Configuration.nYears-1) +".")
        if (fin<Configuration.firstYear) or (fin>=Configuration.firstYear+Configuration.nYears):
            raise Exception("fin("+str(fin)+") must be between "+
                str(Configuration.firstYear) + " and " + str(Configuration.firstYear+Configuration.nYears-1) +".")
        if (ini>fin):
            raise Exception("fin("+fin+") must be greater than ini("+
                str(ini) + ".")
        data = np.zeros((2, fin-ini+1))
        for i in range(ini, fin+1):
            dat = self.getAbsYear(i)
            data[0][i-Configuration.firstYear]=dat[0]
            data[1][i-Configuration.firstYear]=dat[1]
        return data

    def getRelData(self, ini, fin):
        if (ini<Configuration.firstYear) or (ini>=Configuration.firstYear+Configuration.nYears):
            raise Exception("ini("+str(ini)+") must be between "+
                str(Configuration.firstYear) + " and " + str(Configuration.firstYear+Configuration.nYears-1) +".")
        if (fin<Configuration.firstYear) or (fin>=Configuration.firstYear+Configuration.nYears):
            raise Exception("fin("+str(fin)+") must be between "+
                str(Configuration.firstYear) + " and " + str(Configuration.firstYear+Configuration.nYears-1) +".")
        if (ini>fin):
            raise Exception("fin("+fin+") must be greater than ini("+
                str(ini) + ".")
        data = np.zeros(fin-ini+1)
        for i in range(ini, fin+1):
            dat = self.getRelYear(i)
            data[i-Configuration.firstYear]=dat[0]
        return data

    def _detectConstraints(self, i, dat):
        if hasattr(self,"maxDecr") and dat < self.maxDecr:
            self.constrained[i] = True
            return self.maxDecr
        if hasattr(self,"maxIncr") and dat > self.maxIncr:
            self.constrained[i] = True
            return self.maxIncr
        return dat

    def step(self):
        #@todo: Detect constraint violation!
        self.currentStep+=1
        self.m[self.currentStep] = self._detectConstraints(self.currentStep, self.m[self.currentStep])
        #return self.m[self.currentStep]

class PredeterminedSector(Sector):
    ## data in percentages: 5(%) => +0.05

    def __init__(self, sectorID, sectorData):
        super().__init__(sectorID, sectorData)
        IncrS = [0] + [sectorData['data'][i] for i in range(2020,2030)]
        self.m = np.array(IncrS)/100

class InterpolatedSector(Sector):
    def __init__(self, sectorID, sectorData):
        super().__init__(sectorID, sectorData)
        self.maxIncr = sectorData["maxIncr"]/100
        self.maxDecr = sectorData["maxDecr"]/100
        self.m = np.zeros(Configuration.nYears)
        ini = Configuration.firstYear-1
        data = sectorData["data"]
        if ini in data:
            iniData = eval("self."+sectorData["indV"]+'0')
            if data[ini]!=eval("self."+sectorData["indV"]+'0'):
                raise Exception(sectorID + ": Non conformant "+
                    sectorData["indV"]+
                    "0 from data ("+ str(data[ini])
                    +") and sector data ("+ str(iniData) +")")
        if sectorData["indV"]!='e' and sectorData["indV"]!='t':
            raise Exception(sectorID + ": indV is not well defined (" + sectorData["indV"] +")")
        data[ini] = self.t0
        keys = list(data)
        if ini in keys:
            keys.remove(ini)
        if Configuration.lastYear not in keys:
            data[Configuration.lastYear] = self.tf
            keys.append(Configuration.lastYear)
        i = 0
        for dataEntry in sorted(keys):
            fin=dataEntry
            if ini>fin:
                raise Exception(sectorID + ": ini > fin keys in Interpolation.")
            interp = self.__linearInterp(data[ini], data[fin], int(fin)-int(ini))
            for dat in interp:
                year = Configuration.firstYear + i
                if (year > Configuration.firstYear-1):
                    self.m[i] += dat
                i += 1
            ini=fin
    
    def __linearInterp(self, ini, fin, steps):
        interp = np.zeros(steps)
        difStepAbs=(fin-ini)/steps
        val = ini
        if val==0:
            print("__linearInterp: Divide by zero avoided (val=0.0001; ini="+ str(ini)+"; fin=" + str(fin) + ")")
            val = 0.0001
        for i in range(steps):
            interp[i] += difStepAbs/val
            val += val*interp[i]
        return interp

class DependentSector(Sector):
    ## AssSector must be the ID of the sector

    def __init__(self, sectorID, sectorData):
        super().__init__(sectorID, sectorData)
        cfg = Configuration()
        data = sectorData["data"]
        self.maxIncr = sectorData["maxIncr"]/100
        self.maxDecr = sectorData["maxDecr"]/100
        self.assSectorIDs = data["assSector"]
        self.assSectorObjs = []
        self.g = data["g"]
        self.m = np.zeros(Configuration.nYears);

    def step(self):
        if (self.assSectorObjs == None) or (self.assSectorObjs==[]):
            raise Exception(self.sectorID + ": associated sector not defined.")
        self.currentStep+=1
        year = Configuration.firstYear + self.currentStep
        incr = 0
        for assSectorObj in self.assSectorObjs:
            incr += assSectorObj[year][0]
        self.m[self.currentStep]=self._detectConstraints(self.currentStep, self.g*incr)
        #return self.m[self.currentStep]
