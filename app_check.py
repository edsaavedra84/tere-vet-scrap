from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.chrome.options import Options 
import time
import Email
import schedule
import logging
import os

file_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=file_path+'/bot.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def pinchaLaX(driver, step):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'rwCommands')))
        lax = driver.find_element(By.CLASS_NAME, "rwCommands")
        lax.click()  
        time.sleep(1)  
        driver.get_screenshot_as_file("screenshot"+str(step)+".png")
    except:
        driver.get_screenshot_as_file("screenshot-err.png") #meh for now just take the last found success... :P

def job():
    logging.warning("Starting job")
    options = webdriver.ChromeOptions()

    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    options.add_argument('--user-agent="'+agent+'"')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    # this parameter tells Chrome that 
    # it should be run without UI (Headless) 
    options.add_argument("--start-maximized")
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')

    # Set up Selenium WebDriver (you need to have a WebDriver executable installed, like chromedriver)
    driver = webdriver.Chrome(options=options)

    # Navigate to the webpage
    driver.get("https://ebusiness.avma.org/ECFVG/AVMACPEStatusReview.aspx")

    # Perform actions on the webpage (e.g., filling out a form)
    elementUser = driver.find_element(By.ID, "txtUserID")
    elementUser.send_keys("teresitaarayaa@gmail.com")

    elementPass = driver.find_element(By.ID, "txtPassword")
    elementPass.send_keys("yohasakura12")

    element = driver.find_element(By.ID, "ctl12_cmdLogin")
    time.sleep(1)
    # Simulate submitting the form
    element.click()
    pinchaLaX(driver, 1)

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl13_tblMain')))
        driver.get("https://ebusiness.avma.org/ECFVG/AVMACPEStatusReview.aspx")
    except:
        print("regular way...")

    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl13_btnSelectSchedule')))
    scheduleSel = driver.find_element(By.ID, "ctl13_btnSelectSchedule")
    scheduleSel.click()

    pinchaLaX(driver, 2)

    miss = driver.find_element(By.ID, "C003_dlv_rblExamDate_0")
    vegas = driver.find_element(By.ID, "C003_dlv_rblExamDate_1")

    tablesSizes = [len(miss.find_elements(By.CSS_SELECTOR, 'tr')), len(vegas.find_elements(By.CSS_SELECTOR, 'tr'))]
    tablesNames = ["C003_dlv_rblExamDate_0", "C003_dlv_rblExamDate_1"]
    wawa = True # just for testing purposes

    for index in range(len(tablesSizes)):
        # has to be by index and not by element
        for indexRow in range(0, tablesSizes[index]):
            time.sleep(1)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'C003_dlv_rblExamDate_0')))
            table = driver.find_element(By.ID, tablesNames[index])
            row = table.find_elements(By.CSS_SELECTOR, 'tr')[indexRow]

            cells = row.find_elements(By.TAG_NAME, 'td')[0]
            input = cells.find_elements(By.TAG_NAME, 'input')[0]
            date = cells.find_elements(By.TAG_NAME, 'label')[0]

            date_text = date.text.split("-")[0].strip()
            date_obj = datetime.strptime(date_text, '%b %d, %Y')

            if date_obj.month >=7 : #if in range
                row.click()
                step = 3+(index*indexRow)
                pinchaLaX(driver, step)
                time.sleep(1)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'grdSectionInfo')))
                results_table = driver.find_element(By.ID, "grdSectionInfo")

                count = 0
                for row_Table in results_table.find_elements(By.CSS_SELECTOR, 'tr'):
                    count +=1
                    if count == 2:
                        cells_Table = row_Table.find_elements(By.TAG_NAME, 'td')[1]
                        print(cells_Table.text)
                        if wawa == True:
                            Email.sendMail("screenshot"+str(step)+".png")
                            wawa = False

                        if int(cells_Table.text) > 0:
                            print(date_text + "-> avisa ctm ->" + cells_Table.text)
                            logging.warning(date_text + "-> avisa ctm ->" + cells_Table.text)
                            Email.sendMail("screenshot"+str(step)+".png")

    # Close the browser
    driver.quit()   

    schedule.every(1).minutes.do(job)

    return schedule.CancelJob

def main():
    logging.warning("Starting bot jobs...")
    job()

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()    
