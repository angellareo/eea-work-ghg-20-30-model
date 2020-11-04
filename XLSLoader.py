import  xlrd
import  re
import  os, sys, os.path 
import  csv, yaml
import numpy as np

class XLSLoader:
    def __init__(self, infilename):
        re_excelfilename = re.compile(r'(\.xls)$')

        tables = self.xlrd_xls2array(infilename)
        (outdir, infilebase) = os.path.split(infilename)
        outfilebase = re_excelfilename.sub('', infilebase)

        self.yamlOutput = {'runName': outfilebase}
        self.yamlOutput['sectorIDs'] = self.getDataColumn(np.array(tables[0]['sheet_data']),'ID Sector').tolist()
        self.yamlOutput['e0'] = self.getDataColumn(np.array(tables[0]['sheet_data']),'E0').tolist()
        self.yamlOutput['t0'] = self.getDataColumn(np.array(tables[0]['sheet_data']),'T0').tolist()
        scenarios = {}
        for scenario in tables:
            sceName = scenario['sheet_name']
            sceTable = np.array(scenario['sheet_data'])
            sceData = self.loadScenario(sceName,sceTable)
            scenarios[sceName] = sceData
        self.yamlOutput['Scenarios'] = scenarios

    def xlrd_xls2array(self,infilename):
        """ Returns a list of sheets; each sheet is a dict containing
        * sheet_name: unicode string naming that sheet
        * sheet_data: 2-D table holding the converted cells of that sheet
        """
        book       = xlrd.open_workbook(infilename)
        sheets     = []
        formatter  = lambda t, v: self.format_excelval(book,t,v,False)
        
        for sheet_name in book.sheet_names():
            raw_sheet = book.sheet_by_name(sheet_name)
            data      = []
            for row in range(raw_sheet.nrows):
                (types, values) = (raw_sheet.row_types(row), raw_sheet.row_values(row))
                data.append(list(map(formatter, types, values)))
            sheets.append({ 'sheet_name': sheet_name, 'sheet_data': data })
        return sheets

    def format_excelval(self,book, type, value, wanttupledate):
        """ Clean up the incoming excel data """
        ##  Data Type Codes:
        ##  EMPTY   0
        ##  TEXT    1 a Unicode string 
        ##  NUMBER  2 float 
        ##  DATE    3 float 
        ##  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE 
        ##  ERROR   5 
        returnrow = []
        if   type == 2: # TEXT
            if value == int(value): value = int(value)
        elif type == 3: # NUMBER
            datetuple = xlrd.xldate_as_tuple(value, book.datemode)
            value = datetuple if wanttupledate else tupledate_to_isodate(datetuple)
        elif type == 5: # ERROR
            value = xlrd.error_text_from_code[value]
        return value

    def tupledate_to_isodate(self, tupledate):
        """
        Turns a gregorian (year, month, day, hour, minute, nearest_second) into a
        standard YYYY-MM-DDTHH:MM:SS ISO date.  If the date part is all zeros, it's
        assumed to be a time; if the time part is all zeros it's assumed to be a date;
        if all of it is zeros it's taken to be a time, specifically 00:00:00 (midnight).

        Note that datetimes of midnight will come back as date-only strings.  A date
        of month=0 and day=0 is meaningless, so that part of the coercion is safe.
        For more on the hairy nature of Excel date/times see http://www.lexicon.net/sjmachin/xlrd.html
        """
        (y,m,d, hh,mm,ss) = tupledate
        nonzero = lambda n: n!=0
        date = "%04d-%02d-%02d"  % (y,m,d)    if filter(nonzero, (y,m,d))                else ''
        time = "T%02d:%02d:%02d" % (hh,mm,ss) if filter(nonzero, (hh,mm,ss)) or not date else ''
        return date+time

    def printData(self):
        print(self.yamlOutput)

    def getData(self):
        return self.yamlOutput

    def getNpIndex(self, table, element):
        aux = np.where(table == element)[0]
        if len(aux)>0:
            return aux[0]
        else:
            raise Exception("Not found column \"" + str(element) +"\" in table")

    def getDataColumn(self, table, element):
        col = self.getNpIndex(table[0],element)
        return table[1:,col]

    def isPredeterminedSector(self, table):
        ini = self.getNpIndex(table[0],'2020')
        fin = self.getNpIndex(table[0],'2030')
        if ('' in table[1,ini:fin]):
            return False
        else:
            return True

    def isInterpolatedSector(self, table):
        ini = self.getNpIndex(table[0],'2020')
        fin = self.getNpIndex(table[0],'2030')
        if ('' in table[1,ini:fin-1]):
            if (table[1,fin]!=''):
                return True
        else:
            return False

    def isDependentSector(self, table):
        iG = self.getNpIndex(table[0],'G')
        iAssSec = self.getNpIndex(table[0],'Ass. Sector')
        if table[1,iAssSec]!='' and table[1,iG]!='':
            assSecsList = table[1,iAssSec].split('/')
            for assSec in assSecsList:
                if assSec not in self.yamlOutput['sectorIDs']:
                    raise Exception(table[1,iAssSec] + " is not a valid associable sector.")
            return True
        else:
            return False

    def loadPredeterminedSector(self, table):
        ini = self.getNpIndex(table[0],'2020')
        fin = self.getNpIndex(table[0],'2030')
        iMaxIncr = self.getNpIndex(table[0],'MaxIncr')
        iMaxDecr = self.getNpIndex(table[0],'MaxDecr')
        iE0 = self.getNpIndex(table[0],'E0')
        iT0 = self.getNpIndex(table[0],'T0')
        iIndV = self.getNpIndex(table[0],'indV')
        sectorData = {'indV': table[1,iIndV].lower(),
                    'e0': float(table[1,iE0]),
                    't0': float(table[1,iT0]),
                    'mf': float(table[1,fin]),
                    'type': 'Predetermined',
                    'maxIncr': float(table[1,iMaxIncr]),
                    'maxDecr': float(table[1,iMaxDecr]),
                    'data': {}
                    }
        i=ini
        for data in table[1,ini:fin]:
            if data!='':
                sectorData['data'][int(table[0,i])] = float(data)
            else:
                raise Exception("Data missing in predetermined sector")
            i+=1
        return sectorData;

    def loadInterpolatedSector(self, table):
        ini = self.getNpIndex(table[0],'2020')
        fin = self.getNpIndex(table[0],'2030')
        iMaxIncr = self.getNpIndex(table[0],'MaxIncr')
        iMaxDecr = self.getNpIndex(table[0],'MaxDecr')
        iE0 = self.getNpIndex(table[0],'E0')
        iT0 = self.getNpIndex(table[0],'T0')
        iIndV = self.getNpIndex(table[0],'indV')
        if table[1,iMaxIncr]=="":
            table[1,iMaxIncr]="0"
        if table[1,iMaxDecr]=="":
            table[1,iMaxDecr]="0"
        sectorData = {'indV': table[1,iIndV].lower(),
                    'e0': float(table[1,iE0]),
                    't0': float(table[1,iT0]),
                    'mf': float(table[1,fin]),
                    'type': 'Interpolated',
                    'maxIncr': float(table[1,iMaxIncr]),
                    'maxDecr': float(table[1,iMaxDecr]),
                    'data': {}
                    }
        i=ini
        for data in table[1,ini:fin]:
            if data!='':
                sectorData['data'][int(table[0,i])] = float(data)
            i+=1
        return sectorData;

    def loadDependentSector(self, table):
        fin = self.getNpIndex(table[0],'2030')
        iG = self.getNpIndex(table[0],'G')
        iAssSec = self.getNpIndex(table[0],'Ass. Sector')
        iMaxIncr = self.getNpIndex(table[0],'MaxIncr')
        iMaxDecr = self.getNpIndex(table[0],'MaxDecr')
        iE0 = self.getNpIndex(table[0],'E0')
        iT0 = self.getNpIndex(table[0],'T0')
        iIndV = self.getNpIndex(table[0],'indV')
        sectorData = {'indV': table[1,iIndV].lower(),
                    'e0': float(table[1,iE0]),
                    't0': float(table[1,iT0]),
                    'mf': float(table[1,fin]),
                    'type': 'Dependent',
                    'maxIncr': float(table[1,iMaxIncr]),
                    'maxDecr': float(table[1,iMaxDecr]),
                    'data': {'assSector': table[1,iAssSec],
                            'g': float(table[1,iG])
                            }
                    }
        return sectorData;

    def loadSector(self, table):
        if self.isDependentSector(table):
            #return({'type':'DependentSector'});
            sector=self.loadDependentSector(table)
        elif self.isInterpolatedSector(table):
            #return({'type':'InterpolatedSector'});
            sector=self.loadInterpolatedSector(table)
        elif self.isPredeterminedSector(table):
            #return({'type':'PredeterminedSector'});
            sector=self.loadPredeterminedSector(table)
        elif True:
            sectorID = getDataColumn(table,'ID Sector')
            raise Exception("Error defining sector type in sector" + sectorID)
        return sector;

    def loadScenario(self, sceName,sceTable):
        indVs = self.getDataColumn(sceTable,'indV')
        mfAux = self.getDataColumn(sceTable,'2030')
        e0=self.getDataColumn(sceTable,'E0').astype(np.float)
        t0=self.getDataColumn(sceTable,'T0').astype(np.float)
        for i in range(len(mfAux)):
            if mfAux[i]=="":
                if indVs[i]=="E":
                    mfAux[i] = str(e0[i])
                if indVs[i]=="T":
                    mfAux[i] = str(t0[i])
        mf = mfAux.astype(np.float)
        et = e0/self.getDataColumn(sceTable,'T0').astype(np.float)
        for i in np.where(indVs == 'T')[0]:
            mf[i] = mf[i]*et[i]
        scenario = {'ef': mf.tolist()}
        sectors = {}
        i=1
        for sectID in sceTable[1:,self.getNpIndex(sceTable,'ID Sector')]:
            sectors[sectID] = self.loadSector(sceTable[[0,i],:])
            i+=1
        scenario['Sectors'] = sectors
        return scenario