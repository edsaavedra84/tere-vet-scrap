from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service 
import time
import Email
import schedule
import logging
import os

# ugh global var, whatever xD
times_ran = 0
file_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=file_path+'/bot.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

MINUTES_BETWEEN_RETRY = 15

def pinchaLaX(driver, step, ss_folder):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'rwCommands')))
        lax = driver.find_element(By.CLASS_NAME, "rwCommands")
        lax.click()  
        time.sleep(1)  
        driver.get_screenshot_as_file(file_path+"/"+ss_folder+"/screenshot"+str(step)+".png")
    except:
        driver.get_screenshot_as_file(file_path+"/"+ss_folder+"/screenshot-err.png") #meh for now just take the last found success... :P

def get_options():
    options = webdriver.ChromeOptions()

    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    options.add_argument('--user-agent="'+agent+'"')
    options.add_argument("--window-size=1280,1024")
    options.add_argument("--disable-extensions")
    # this parameter tells Chrome that 
    # it should be run without UI (Headless) 
    options.add_argument("--start-maximized")
    options.add_argument('--headless=new') # walala ahora funciono xD
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')

    return options

def job():
    try: 
        global times_ran

        #once a day send a warning that we are running over email, (for now every 96 runs = 24hrs)
        if times_ran % ((60 / MINUTES_BETWEEN_RETRY) * 24) == 0:
            logging.warning("Warn that we are running! -> times_ran=%s, vs=%s", str(times_ran), str((60 / MINUTES_BETWEEN_RETRY)*24))
            Email.sendMailRunning()      

        times_ran += 1

        datetime_object = datetime.now()
        formatted_datetime = datetime_object.strftime("%Y%m%d-%H%M%S")

        logging.warning("------------------------------")
        logging.warning("Run id: %s", formatted_datetime)
        logging.warning("Run number: %s", str(times_ran))
        logging.warning("------------------------------")
        logging.warning("Starting job")

        # Set up Selenium WebDriver (you need to have a WebDriver executable installed, like chromedriver)
        if os.name == 'win32' or os.name == 'nt':  
            driver = webdriver.Chrome(options=get_options())
        else:
            # assume linux
            service = webdriver.ChromeService(executable_path="/usr/lib/chromium-browser/chromedriver")
            driver = webdriver.Chrome(options=get_options(), service=service)

        # create folder to store screenshots
        try:
            os.makedirs(file_path+"/"+formatted_datetime)
        except FileExistsError:
            # directory already exists
            pass

        # Navigate to the webpage
        try:
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
            pinchaLaX(driver, 1, formatted_datetime)
        except Exception as e:
            logging.warning("Fail to get initial page, retry in 30 secs, could be comm loss or something, %s", e)
            schedule.every(30).seconds.do(job)

            return schedule.CancelJob

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl13_tblMain')))
            driver.get("https://ebusiness.avma.org/ECFVG/AVMACPEStatusReview.aspx")
        except:
            logging.warning("regular way...")

        time.sleep(1)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl13_btnSelectSchedule')))
        scheduleSel = driver.find_element(By.ID, "ctl13_btnSelectSchedule")
        scheduleSel.click()

        pinchaLaX(driver, 2, formatted_datetime)

        miss = driver.find_element(By.ID, "C003_dlv_rblExamDate_0")
        vegas = driver.find_element(By.ID, "C003_dlv_rblExamDate_1")

        tablesSizes = [len(miss.find_elements(By.CSS_SELECTOR, 'tr')), len(vegas.find_elements(By.CSS_SELECTOR, 'tr'))]
        tablesNames = ["C003_dlv_rblExamDate_0", "C003_dlv_rblExamDate_1"]
        foundSomething = False

        for index in range(len(tablesSizes)):
            # has to be by index and not by element
            logging.warning("Checking table: %s", tablesNames[index])

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
                    pinchaLaX(driver, step, formatted_datetime)
                    time.sleep(1)
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'grdSectionInfo')))
                    results_table = driver.find_element(By.ID, "grdSectionInfo")
                    # Email.sendMail(file_path+"/"+formatted_datetime+"/screenshot"+str(step)+".png") #test
                    count = 0
                    for row_Table in results_table.find_elements(By.CSS_SELECTOR, 'tr'):
                        count +=1 #unnecesary but meh!
                        if count == 2:
                            cells_Table = row_Table.find_elements(By.TAG_NAME, 'td')[1]
                            logging.warning("%s -> %s", date_text, cells_Table.text)
                            print(date_text + " -> " + cells_Table.text)

                            if cells_Table.text.strip() != "0":
                                foundSomething = True

                            try:
                                if int(cells_Table.text) > 0:
                                    logging.warning("%s -> avisa ctm -> %s", date_text, cells_Table.text)
                                    Email.sendMail(file_path+"/"+formatted_datetime+"/screenshot"+str(step)+".png")

                            except Exception as e:
                                logging.error('Error: %s', e)
                                #maybe is not an int?
                                logging.warning("Something strange happened, value: %s, check and send email", cells_Table.text)
                                logging.warning("%s -> avisa ctm -> %s", date_text, cells_Table.text)
                                Email.sendMail(file_path+"/"+formatted_datetime+"/screenshot"+str(step)+".png")

        # Close the browser
        driver.quit()   

        if foundSomething == True:
            logging.warning("something was found!")
        else:
            logging.warning("Nothing found :(")

        schedule.every(MINUTES_BETWEEN_RETRY).minutes.do(job)

        return schedule.CancelJob

    except Exception as e:
        logging.error("------->>>>>>>>")
        logging.error('Something out of the norm happened, will reattempt later: %s', e)
        logging.error("------->>>>>>>>")

        schedule.every(MINUTES_BETWEEN_RETRY * 2).minutes.do(job)

        return schedule.CancelJob

def main():
    global times_ran

    logging.warning("Starting bot jobs...")
    job()

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()    
