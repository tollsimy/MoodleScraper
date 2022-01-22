from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import urllib.request
import os
import sys
import time
import argparse
from getpass import getpass
from pathlib import Path
import platform

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count * block_size * 100 / total_size),100)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

opsys=platform.system()

parser = argparse.ArgumentParser(description="Download all Kaltura videos from a UniTN Moodle page.")
parser.add_argument('-v', '--verbose' ,help="verbose", required=False, action='append_const', const=1)
parser.add_argument("Page_URL",help="Moodle Page link",type=str)
args=parser.parse_args()

USERNAME=input("Enter username: ")
PASSWORD=getpass()
verbose=args.verbose
COURSEPAGE=args.Page_URL
LOGINPAGE="https://didatticaonline.unitn.it/dol/loginUniTN.php"

#set driver
try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if(verbose==None):
        options.headless = True
    if(opsys=="Windows"):
        ser=Service(os.getcwd()+str(Path("\\bin\\chromedriver_WIN32.exe")))
        browser = webdriver.Chrome(options=options, service=ser)
    elif(opsys=="Linux"):
        ser=Service(os.getcwd()+str(Path("\\bin\\chromedriver_LINUX64")))
        browser = webdriver.Chrome(options=options,service=ser)
    elif(opsys=="Darwin"):
        if(platform.architecture=="arm"):
            ser=Service(os.getcwd()+str(Path("/bin/chromedriver_MAC_M1")))
            browser = webdriver.Chrome(options=options,service=ser)
        else:
            print(os.getcwd()+str(Path("/bin/chromedriver_MAC64")))
            ser=Service(os.getcwd()+str(Path("/bin/chromedriver_MAC64")))
            browser = webdriver.Chrome(options=options,service=ser)

except Exception as e :
    print(e)
    print("ERROR: 'chromedriver.exe' not found")
    sys.exit()
if(verbose==None):
    print("Starting Chrome silently...")
else:
    print("Starting Chrome...")

#get login page
browser.get(LOGINPAGE)
try:
    LOGINPAGE=browser.find_element(by=By.ID, value="btn-login-unitn-it" )
    LOGINPAGE.click()
    wait = WebDriverWait( browser, 5 )

    #login page
    login = browser.find_element(by=By.NAME, value="j_username")
    login.send_keys(USERNAME)

    password = browser.find_element(by=By.NAME, value="j_password")
    password.send_keys(PASSWORD)

    accedi = browser.find_element(By.ID, value="btnAccedi")
    pagina=browser.current_url
    accedi.click()
    wait = WebDriverWait( browser, 5 )
    if(pagina[0:-4]==browser.current_url[0:-4]):
        print("ERROR: Wrong username or password!")
        sys.exit()
    print("Logging in...")

    #get course page
    browser.get(COURSEPAGE)

    topics = browser.find_elements(By.CLASS_NAME, value="aalink")

    print("Searching for Kaltura videos...")

    videos = {"name":"link"}
    for topic in topics:
        if "Kaltura Video Resource" in topic.text:
            name=topic.text.replace("Kaltura Video Resource","")  #remove useless chars
            name=name[0:-1]                                         #remove \n
            videos[name]=topic.get_attribute("href")
        elif "Kaltura Video Presentation" in topic.text:
            name2=topic.text.replace("Kaltura Video Presentation","")   #remove useless chars
            name2=name2[0:-1]                                           #remove \n
            videos[name2]=topic.get_attribute("href")

    videos.pop("name")   #remove first useless pair

    print("Found " + str(len(videos))+ " videos...")
    print("Starting downloads...")
    p = Path("Videos/")
    p.mkdir(parents=True, exist_ok=True)

    i=1
    for key in videos :
        #go to video page
        browser.get(videos[key])
        browser.implicitly_wait(10)     #wait for video page to load

        #get video link
        try:
            browser.switch_to.frame("contentframe")
            browser.switch_to.frame("kplayer_ifp")
        except Exception as e:
            print("W: One ore more frames not found, please wait...")
        try:
            linkElem = browser.find_element(By.ID, value="pid_kplayer")
            link=linkElem.get_attribute("src")
        except Exception as e:
            print("W: pid_kplayer not found, please wait...")
            browser.switch_to.default_content()
            link=browser.find_element(By.XPATH,value=('//*[@id="contentframe"]')).get_attribute('src')

        #download video from source page
        cwd = os.getcwd()
        filename=key.replace("/", "-")
        path=cwd+str(Path("\\Videos\\" +filename +".mp4"))
        start_time=time.time()
        urllib.request.urlretrieve(link, path, reporthook)
        print("\n"+"Video "+ str(i)+" of " + str(len(videos)) + " downloaded please wait...")
        i=i+1

    print("Download complete, thanks for flying with us!")
except Exception as e:
    print("ERROR: page not compatible")
    print(e)
    sys.exit()
browser.close()
