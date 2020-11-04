import xlwt
import numpy as np

class XLSWriter:
    def __init__(self, scenarios):
        self.scenarios = scenarios
        self.totalEIni = 0
        self.totalE = np.zeros(11)
        self.totalT = np.zeros(11)

    def dump(self, filename):
        xlsBook = xlwt.Workbook()
        for scenario in self.scenarios:
            scenarioSh = xlsBook.add_sheet(scenario.name)
            self.addHeader(scenarioSh);
            i=1
            for sector in scenario.sectorsP:
                self.addSector(scenarioSh,i,sector)
                i+=1
            self.printRow(scenarioSh, i, 17, self.totalE)
            self.printRow(scenarioSh, i, 29, self.totalT)
            scenarioSh.write(i+1,27,100-(100*self.totalE[10]/self.totalEIni))
        xlsBook.save(filename)

    def printRow(self,currentSheet,row,iniCol,data):
        i=0
        for dat in data:
            currentSheet.write(row,iniCol+i,dat)
            i+=1

    def addHeader(self,currentSheet):
        header = ['Subsector', 'E₀ (2017/Tg)', 'T₀ (2017/horas)', 'E/T (Tg/h)',  'Matriz de tasa de cambio por sector (%)',
            '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030',
            'Valores absolutos emisión por sector (Tg)',
            '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030',
            'Valores absolutos hora por sector (h)',
            '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
        i = 0
        font = xlwt.Font()
        font.bold = True
        style = xlwt.XFStyle()
        style.font = font
        for dat in header:
            currentSheet.write(0,i,dat,style=style)
            i+=1

    def addSector(self,currentSheet,iSector,sector):
        iniData = [sector.name, sector.e0, sector.t0, sector.eTConstant]
        relData = sector.getRelData(2020,2030).tolist()
        absData = sector.getData(2020,2030).tolist()
        normalStyle = xlwt.easyxf('font: bold 0;')
        redStyle = xlwt.easyxf('font: bold 0, color red;')

        self.totalEIni += sector.e0

        style = normalStyle
        i = 0
        j = 0
        for dat in iniData:
            if isinstance(dat, str):
                currentSheet.write(iSector,i,dat,style=style)
            else:
                currentSheet.write(iSector,i,float(dat),style=style)
            i+=1
            j+=1
        j = 0

        currentSheet.write(iSector,i,'')
        i+=1
        
        for dat in relData:
            if sector.constrained[j]:
                style = redStyle
            else:
                style = normalStyle
            if isinstance(dat, str):
                currentSheet.write(iSector,i,dat,style=style)
            else:
                currentSheet.write(iSector,i,float(dat),style=style)
            i+=1
            j+=1
        j = 0

        currentSheet.write(iSector,i,'')
        i+=1

        for dat in absData[0]:
            if sector.constrained[j]:
                style = redStyle
            else:
                style = normalStyle
            if isinstance(dat, str):
                currentSheet.write(iSector,i,dat,style=style)
            else:
                currentSheet.write(iSector,i,float(dat),style=style)
            self.totalE[j] += float(dat)
            i+=1
            j+=1
        j=0

        currentSheet.write(iSector,i,'')
        i+=1

        for dat in absData[1]:
            if sector.constrained[j]:
                style = redStyle
            else:
                style = normalStyle
            if isinstance(dat, str):
                currentSheet.write(iSector,i,dat,style=style)
            else:
                currentSheet.write(iSector,i,float(dat),style=style)
            self.totalT[j] += float(dat)
            i+=1
            j+=1
        j=0

