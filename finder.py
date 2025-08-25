import matplotlib as mplot
import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np
import sqlite3 as sql
from scraper import ex
import time

def populate_map(curs, name) :
    map = dict()
    s = f"SELECT * FROM {name};"
    curs.execute(s)
    for row in curs.fetchall():
        map[row[0]] = row[1]
    return map

def populate_type_list(curs, name, colname) :
    lst = list()
    curs.execute(f"SELECT {colname} FROM {name};")
    for row in curs.fetchall():
        if(row[0] != None and row[0] not in lst):
            lst.append(row[0])
    return lst

nex1 = sql.connect('data.db')
nex2 = sql.connect('maps.db')
curs1 = nex1.cursor()
curs2 = nex2.cursor()
ctoa = populate_map(curs2, 'ctoa')
ctov = populate_map(curs2, 'ctov')
tl = dict()
while True:
    print("Filtering options (type DONE to finish):")
    i = 0
    listnums_to_atts = dict()
    for code, att in ctoa.items():
        i += 1
        print(f"{i}. {att}")
        listnums_to_atts[i] = code
        if i > 19: 
            break
    try :
        inp = input()
        if(inp == "DONE"):
            break
        inp = int(inp)
    except ValueError:
        print("Invalid input. Please enter a number.")
        nex1.close()
        nex2.close()
        exit()
    if not inp in listnums_to_atts: 
        print("Invalid selection. Enter a number from 1 to 200.")
        nex1.close()
        nex2.close()
        exit()
    code = listnums_to_atts[inp]
    print(f"Selected number: {inp}, corresponding to code {code} ({ctoa[code]})")
    print("What type of language do you want to see?")
    code_swap = str()
    try : 
        nonsense = str(int(code[:-1]))
        code_swap = "C" + code
    except ValueError:
        code_swap = ctoa[code]
    types = populate_type_list(curs1, "languagetable", code_swap)
    print("Available types:")
    i = 0
    temp_ntot = dict()
    for type in types:
        i += 1
        print(f"{i}: {type}")
        temp_ntot[i] = type
    try :
        inp = input()
        if(inp == "DONE"):
            break
        inp = int(inp)
    except ValueError:
        print("Invalid input. Please enter a number.")
        nex1.close()
        nex2.close()
        exit()
    if not inp in temp_ntot:
        print(f"Invalid type. Please enter a number from 1 to {len(temp_ntot)}")
        nex1.close()
        nex2.close()
        exit()
    print(f"Selected type: {temp_ntot[inp]}")
    tl[code] = temp_ntot[inp]
    print("\nCurrent filter list:")
    for attc, spec in tl.items():
        print(f"{ctoa[attc]}: {spec}")
    print("\nContinuing filtering...")
    time.sleep(3)
print("Final filter list:")
for attc, spec in tl.items():
    print(f"{ctoa[attc]}: {spec}")
print("Generating list...")
multiline = "SELECT * FROM languagetable WHERE "
for attc, spec in tl.items():
    if multiline[-1] != " ":
        multiline += " AND "
    if attc == -7 or attc == -8:
        multiline += f"({ctoa[attc]} = {spec})"
    else:   
        try:
            nonsense = int(attc)
            multiline += f"({ctoa[attc]} = '{spec}')"
        except ValueError:
            cattc = "C" + attc
            multiline += f"({cattc} = '{spec}')"
multiline += ";"
curs1.execute(multiline)
lst = curs1.fetchall()
lang_str =  "language" if len(lst) == 1 else "languages"
print(f"Found {len(lst)} {lang_str} matching your criteria")
for row in lst:
    print(row[1])
nex1.close()
nex2.close()
exit()