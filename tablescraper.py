import sqlite3 as sql
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


url = "https://wals.info/languoid?sEcho=1&iColumns=9&sColumns=name%2Cid%2Ciso_codes%2Cgenus%2Cfamily%2Cmacroarea%2Clatitude%2Clongitude%2Ccountries&iDisplayStart=0&iDisplayLength=100&mDataProp_0=0&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&bRegex_5=false&bSearchable_5=true&bSortable_5=true&mDataProp_6=6&bRegex_6=false&bSearchable_6=true&bSortable_6=true&mDataProp_7=7&bRegex_7=false&bSearchable_7=true&bSortable_7=true&mDataProp_8=8&bRegex_8=false&bSearchable_8=true&bSortable_8=false&bRegex=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&__eid__=Languages&sEcho=1&iColumns=9&sColumns=name%2Cid%2Ciso_codes%2Cgenus%2Cfamily%2Cmacroarea%2Clatitude%2Clongitude%2Ccountries&iDisplayStart=0&iDisplayLength=100&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&mDataProp_7=7&sSearch_7=&bRegex_7=false&bSearchable_7=true&bSortable_7=true&mDataProp_8=8&sSearch_8=&bRegex_8=false&bSearchable_8=true&bSortable_8=false&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&__eid__=Languages&_=1747954291879"
overhead = 9
varcols = 192
colcount = overhead + varcols
rowcount = 2662
perpage = 100
headers = 2

def ex(x, y) :
    x.execute(y)
    return

connection = sql.connect('data.db')
curs = connection.cursor()
ex(curs, "DROP TABLE IF EXISTS languagetable;")
multiline = """CREATE TABLE languagetable (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    LName varchar(255),
    LID varchar(255),
    ISO varchar(255),
    Genus varchar(255),
    Family varchar(255),
    Macroarea varchar(255),
    Latitude double,
    Longitude double,
    Countries varchar(255),"""

for i in range(overhead, colcount) : 
    multiline += "\n    C" + str(i) + " int,"
multiline += "\n    C" + str(colcount) + " int);"
ex(curs, multiline)

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

pn = 0

while True :
    html = driver.page_source
    su = bs(html, "html.parser")
    table = su.find("table")
    rows = table.find_all("tr")[headers:]
    for row in rows:
        cells = row.find_all("td")
        row_data = [cell.get_text(strip=True) for cell in cells[:overhead]]
        multiline = "INSERT INTO languagetable (LName, LID, ISO, Genus, Family, Macroarea, Latitude, Longitude, Countries) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        curs.execute(multiline, row_data)
        #print(row_data)
        
    try :
        npl = driver.find_element(By.CSS_SELECTOR, "li.next > a")
        npl.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        parent_li = npl.find_element(By.XPATH, "..")
        pn += 1
        print("Page " + str(pn) + " processed!")
        if "disabled" in parent_li.get_attribute("class") :
            print("done!")
            break
    except(NoSuchElementException, TimeoutException) :
        break

#ex(curs, """INSERT INTO languagetable VALUES (1, "Finnish", 2, 10);""")
#ex(curs, """INSERT INTO languagetable VALUES (2, "English", 0, 7);""")
connection.commit()
driver.quit()
connection.close()