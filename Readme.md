# Work scenarios in the ecosocial transition - 2020-2030

## Ubuntu installation

Just run the following commands once:

```
cd eea-model

sudo apt-get install python3 python3-pip
sudo pip3 install virtualenv

virtualenv -p /usr/bin/python3 modelenv
source modelenv/bin/activate
pip3 install numpy scipy matplotlib ipython jupyter pandas sympy nose pyyaml xlrd xlwt
```

## Execution

```
source modelenv/bin/activate
python3 main.py
```

To select the input/output file names, modify the following lines in main.py:
```
inputFilename = "Input1.xls"
outputFilename = "Output-1.xls"
```

Red values in the output represent constrained results (by MaxIncr or MaxDecr).

Use `python3 -i main.py` to stay in python command shell after running the script.

To get the name of scenario `n` in the scenario list: `scenarios[n].name`
To get the name of sector `m` in the sector list of scenario `n`: `scenarios[m].name`

You can also get the [e,t] evolution of sector `m` in scenario `n`:
```
scenarios[n].sectorsP[m].getData(iniYear,endYear)
```
For instance: `scenarios[0].sectorsP[0].getData(2020,2030)`

Or if you want to get the increase/decrease percentages year by year:
```
scenarios[0].sectorsP[0].m
```
