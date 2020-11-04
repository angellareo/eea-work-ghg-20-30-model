import numpy as np
import yaml
import sys
from Scenarios import Scenario
from Configuration import Configuration
from XLSLoader import XLSLoader
from XLSWriter import XLSWriter

inputFilename = "Input1.xls"
outputFilename = "Output-2.xls"

print ("\nLOADING")
loader = XLSLoader(inputFilename)
scenarios=[]
for scenarioName in loader.yamlOutput['Scenarios']:
    print ("Loading scenario " + scenarioName + " from "+inputFilename+"...")
    scenarios.append(Scenario(scenarioName,loader.yamlOutput['Scenarios'][scenarioName]))
    print ("OK")

print ("\nRUNNING")
for scenario in scenarios:
    print ("Running scenario " + scenario.name + ":")
    for year in Configuration.years:
        print("\t" + str(year), end=" ")
        for sector in scenario.sectorsP:
            sector.step()
    print("\n")

print ("\nWRITER")
print ("Writing to file: " + outputFilename)
writer = XLSWriter(scenarios)
writer.dump(outputFilename);
