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
url2 = "https://wals.info/feature"
overhead = 9
varcols = 192
colcount = overhead + varcols
rowcount = 2662
perpage = 10
headers = 2
uniqols = 144

nums_to_repetitions = dict([(10, 2), (21, 2), (25, 2), (39, 2), (58, 2), (79, 2), (81, 2), (90, 7), (108, 2), (109, 2), (130, 2), (136, 2), (137, 2), (143, 7), (144, 25)])
nums_to_alpha = dict([(1, "A"), (2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F"), (7, "G"), (8, "H"), (9, "I"), (10, "J"), (11, "K"), (12, "L"), (13, "M"), (14, "N"), (15, "O"), (16, "P"), (17, "Q"), (18, "R"), (19, "S"), (20, "T"), (21, "U"), (22, "V"), (23, "W"), (24, "X"), (25, "Y")])

def get_feature_rows(driver):
    try:
        # Wait for processing to complete (indicates data is loaded)
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "Datapoints_processing"))
        )
        
        # Wait for at least one data row to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#Datapoints tbody tr"))
        )
        
        # Get the HTML after dynamic content has loaded
        html = driver.page_source
        soup = bs(html, 'html.parser')
        
        # Find the specific table by ID
        table = soup.find('table', {'id': 'Datapoints'})
        if not table:
            return []
        
        # Find all rows in the tbody (skipping header rows)
        tbody = table.find('tbody')
        if not tbody:
            return []
        
        return tbody.find_all('tr')
    except Exception as e:
        print(f"Error in get_feature_rows: {e}")
        return []

def next_page(driver) : 
    try :
        npl = driver.find_element(By.CSS_SELECTOR, "li.next > a")
        npl.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        parent_li = npl.find_element(By.XPATH, "..")
        if "disabled" in parent_li.get_attribute("class") :
            return 1
    except(NoSuchElementException, TimeoutException) :
        return 2
    return 0

def get_rows(driver) :
    html = driver.page_source
    su = bs(html, "html.parser")
    table = su.find("table")
    rows = table.find_all("tr")[headers:]
    return rows

def ex(x, y) :
    x.execute(y)
    return

def fill_table_with_dict_(codes_to_atts):
    options = Options()
    #options.add_argument("--headless")

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

    #driver = webdriver.Chrome(options=options)
    #driver.get(url2)
    #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    for i in range(1, uniqols + 1) : 
        if i in nums_to_repetitions.keys() :
            for j in range(1, nums_to_repetitions[i] + 1) :
                multiline += "\n    C" + str(i) + nums_to_alpha[j] + " int,"
        else : 
            multiline += "\n    C" + str(i) + "A int,"
    multiline = multiline[0:-1]
    multiline += ");"
    #print(multiline)
    ex(curs, multiline)

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    pn = 0
    lpf = True
    idx = 0

    cur_first = None

    while True :
        #print("what")
        rows = get_rows(driver)
        if idx + 1 > rowcount : 
            print("Done!")
            break
        while len(rows) == 0 :
            print("No rows found, waiting...")
            time.sleep(10)
            rows = get_rows(driver)
        print(f"Found {len(rows)} rows")
        cur_first = rows[0].find_all("td")[0].get_text(strip=True)
        for row in rows:
            idx += 1
            if idx > rowcount :
                print("done!")
                lpf = False
                break
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells[:overhead]]
            multiline = "INSERT INTO languagetable (LName, LID, ISO, Genus, Family, Macroarea, Latitude, Longitude, Countries) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            curs.execute(multiline, row_data)
            links = cells[0].find_all("a")
            link = links[0].get("href")
            driver.execute_script("window.open(arguments[0]);", link)
            driver.switch_to.window(driver.window_handles[1])
            try:
                feature_rows = get_feature_rows(driver)
                print(f"For {row_data[0]}, found {len(feature_rows)} feature rows")
                
                for brow in feature_rows:
                    bcells = brow.find_all("td")
                    if len(bcells) >= 2:
                        feature_id = bcells[0].get_text(strip=True)
                        feature_value = bcells[1].get_text(strip=True)
                        feature_id = feature_id.replace('.', '').replace(' ', '')
                        fid_i = int(feature_id)
                        codes_to_atts[fid_i] = bcells[2].get_text(strip=True)
                        updater = f"UPDATE languagetable SET C{feature_id} = \"{feature_value}\" WHERE ID = {idx};"
                        print(updater)
                        try:
                            curs.execute(updater)
                        except sql.OperationalError as e:
                            print(f"Error executing: {updater}\n{e}")
                            
            except Exception as e:
                print(f"Error processing language page: {e}")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        if not lpf:
            break
        pcode = next_page(driver)
        time.sleep(10)
        #if(pcode == 0 or lpf) : 
        #   pn += 1
        #    print("Page " + str(pn) + " processed!")
        #if(pcode == 1) :
        #   if(lpf) : 
        #      lpf = False
        # else :
            #    pn += 1
            #   print("done!")
            #  break
    # if(pcode == 2) :
        #    print("wuh-oh!")
        #   break

    #ex(curs, """INSERT INTO languagetable VALUES (1, "Finnish", 2, 10);""")
    #ex(curs, """INSERT INTO languagetable VALUES (2, "English", 0, 7);""")
    connection.commit()
    driver.quit()
    connection.close()

def generate_dicts(codes_to_atts, codes_to_varcols):
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get(url2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    pn = 0
    lpf = True
    idx = 0
    cur_first = None
    while True :
        #print("what")
        rows = get_rows(driver)
        if idx + 1 > varcols: 
            print("Done!")
            break
        while len(rows) == 0 :
            print("No rows found, waiting...")
            time.sleep(10)
            rows = get_rows(driver)
        print(f"Found {len(rows)} rows")
        for row in rows:
            idx += 1
            if idx > rowcount :
                print("done!")
                lpf = False
                break
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells[:overhead]]
            codes_to_atts[row_data[0]] = row_data[1]
            codes_to_varcols[row_data[0]] = idx
        if not lpf:
            break
        pcode = next_page(driver)
        time.sleep(10)
    driver.quit()