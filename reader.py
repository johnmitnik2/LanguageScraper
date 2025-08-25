import sqlite3 as sql
from scraper import generate_dicts as gd
from scraper import ex

nums_to_baseatts = dict()
nums_to_baseatts = {
    -1: "Name",
    -2: "LID",
    -3: "ISO",
    -4: "Genus",
    -5: "Family",
    -6: "Macroarea",
    -7: "Latitude",
    -8: "Longitude"
}

def make_table(map, name): 
    connection = sql.connect('maps.db')
    curs = connection.cursor()
    ex(curs, f"DROP TABLE IF EXISTS {name};")
    ex(curs, f"CREATE TABLE {name} (inp varchar(255), outp varchar(255));")
    if(name == "ctoa") :
        for i in range(-8, 0) :
            try:
                curs.execute(f"INSERT INTO {name} (inp, outp) VALUES (?, ?)", (str(i), nums_to_baseatts[i]))
            except sql.OperationalError as e:
                print(f"Error inserting base attribute {i}: {e}")
    for inp, outp in map.items():
        try:
            curs.execute(f"INSERT INTO {name} (inp, outp) VALUES (?, ?)", (str(inp), str(outp)))
        except sql.OperationalError as e:
            print(f"Error inserting code {inp}: {e}")
    connection.commit()
    connection.close()

nex1 = sql.connect('data.db')
curs1 = nex1.cursor()
curs1.execute("SELECT * FROM languagetable")
codes_to_atts = dict()
codes_to_varcols = dict()
gd(codes_to_atts, codes_to_varcols)
nex1.close()
make_table(codes_to_atts, "ctoa")
make_table(codes_to_varcols, "ctov")
nex2 = sql.connect('maps.db')
curs2 = nex2.cursor()
curs2.execute("SELECT * FROM ctoa")
print("Codes to Attributes:")
for row in curs2.fetchall():
    print(row)
curs2.execute("SELECT * FROM ctov")
print("Codes to Columns:")
for row in curs2.fetchall():
    print(row)
nex2.close()