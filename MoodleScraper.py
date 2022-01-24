import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import urllib.request
import os
import sys
import time
import argparse
from getpass import getpass
from pathlib import Path
import platform
import json

#TODO: use __main__ like normal devs
global video_dict

def hello():
    print('''
███╗   ███╗ ██████╗  ██████╗ ██████╗ ██╗     ███████╗    ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
████╗ ████║██╔═══██╗██╔═══██╗██╔══██╗██║     ██╔════╝    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██╔████╔██║██║   ██║██║   ██║██║  ██║██║     █████╗      ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
██║╚██╔╝██║██║   ██║██║   ██║██║  ██║██║     ██╔══╝      ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██████╔╝███████╗███████╗    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝                                                                                                                        
    ''')       

def write_json(filename, jsonObj):
    try:
        with open(filename+'.json', 'w') as outfile:
            json.dump(jsonObj, outfile, indent=2)
    except Exception as e:
        print(e)

def create_db():
    json_filename = ""
    while(json_filename == ""):
        json_filename = input("Type the name of the course you want to download: ")
    write_json(json_filename, video_dict)

def json2dict(filename):
    with open(str(filename), "r") as read_file:
        dict = json.load(read_file)
        return dict

def show_dict(dict):
    print ("{:<10} {:<10}".format('ID', 'NAME'))
    j = 1   #list start from 1 and not from 0
    for i in dict.items():
        print ("{:<10} {:<10}".format(j, i[0]))
        j+=1

def download_multiple(dict):
    show_dict(dict)
    print("List which videos do you want to download using commas or type 'all' to select all \neg: 1,2,3")
    in_list = input(": ")
    if(in_list != 'all'):
        in_list = list(in_list.split(','))
        for video in in_list:
            index=int(video)-1  #list start from 1 and not from 0
            try:
                print(f"Scarico: {list(dict.keys())[index]}")
                download_single_video(list(dict.keys())[index])
                print("")
            except Exception as e:
                print(e)
    else:
        download_all(dict)


def download_single_video(obj):
    p = Path("Videos") / Path(coursename)
    print(p)
    p.mkdir(parents=True, exist_ok=True)
    global video_dict
    global start_time
    #download video from source page
    cwd = os.getcwd()
    filename=obj.replace("/", "-")
    path=cwd+str(p)+filename +".mp4"
    if(opsys=="Darwin" or opsys=="Linux"):
        path=cwd+str(Path("/Videos/" +filename +".mp4"))
    start_time=time.time()
    urllib.request.urlretrieve(video_dict[obj], path, reporthook)

#download all files
def download_all(dict):
    i = 0
    for j in dict:
        download_single_video(j)
        print("\n"+"Video "+ str(i+1)+" of " + str(len(dict)) + " downloaded please wait...")
        i=i+1

def login():
    global LOGINPAGE
    print("Logging in...")
    #get login page
    browser.get(LOGINPAGE)
    LOGINPAGE=waitAndFind(By.ID,"btn-login-unitn-it")
    LOGINPAGE.click()

    #login page
    login = waitAndFind(By.NAME,"j_username")
    login.send_keys(USERNAME)

    password = waitAndFind(By.NAME,"j_password")
    password.send_keys(PASSWORD)

    accedi = waitAndFind(By.ID,"btnAccedi")
    pagina=browser.current_url
    accedi.click()
    if(pagina[0:-4]==browser.current_url[0:-4]):
        print("ERROR: Wrong username or password!")
        sys.exit()
    

def get_videos():
    global coursename
    global video_dict
    #get course page
    browser.get(COURSEPAGE)

    coursename=waitAndFind(By.TAG_NAME,"h1").text
    coursename.replace("/", "-")
    topics = waitAndFindMultiple(By.CLASS_NAME,"aalink")

    print("Searching for Kaltura videos...")

    videos = {}
    for topic in topics:
        if "Kaltura Video Resource" in topic.text:
            name=topic.text.replace("Kaltura Video Resource","")  #remove useless chars
            name=name[0:-1]                                         #remove \n
            videos[name]=topic.get_attribute("href")
        elif "Kaltura Video Presentation" in topic.text:
            name2=topic.text.replace("Kaltura Video Presentation","")   #remove useless chars
            name2=name2[0:-1]                                           #remove \n
            videos[name2]=topic.get_attribute("href")

    print("Found " + str(len(videos))+ " videos...")
    print("The script will browse through every video to create a download link, it may take a while")
    print("Creating download list...")

    video_dict = {}
    i=1
    for key in videos :
        #go to video page
        browser.get(videos[key])

        #TODO: are emplicity wait really required?
        browser.implicitly_wait(5)     #wait for video page to load

        #get video link
        print(f"Getting video link #{i} of {len(videos)}")
        try:
            selWait(By.ID, "contentframe")
            browser.switch_to.frame("contentframe")
            selWait(By.ID, "kplayer_ifp")
            browser.switch_to.frame("kplayer_ifp")
        except Exception as e:
            print("W: One ore more frames not found, please wait...")
        try:
            linkElem = waitAndFind(By.ID,"pid_kplayer")
            link=linkElem.get_attribute("src")
            video_dict[key] = link
            i+=1
        except Exception as e:
            print("W: pid_kplayer not found, please wait...")
            print(e)
            browser.switch_to.default_content()
            link=waitAndFind(By.XPATH,'//*[@id="contentframe"]').get_attribute('src')

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    if(duration==0.0):
        duration = 0.1
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

USERNAME = ""
PASSWORD = ""
hello()
USERNAME=input("Enter username: ")
PASSWORD=getpass()
verbose=args.verbose
COURSEPAGE=args.Page_URL
LOGINPAGE="https://didatticaonline.unitn.it/dol/loginUniTN.php"

#TODO: wrap all in a try-catch to handle program breaking
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
    sys.exit()
if(verbose==None):
    print("Starting Chrome silently...")
else:
    print("Starting Chrome...")


try:
    choice = 'x'
    filename = ""
    while(choice != 'Y' and choice != 'N' and choice != 'y' and choice != 'n'):
        choice = input("Do you want to download from an existing json file? [Y/N]: ")
    if choice == 'Y' or choice == 'y':
        while(filename == ""):
            filename = input("Type the name of the file (don't include extension): ")
        video_dict = json2dict(filename+'.json')
        login()
        download_multiple(video_dict)
    else:
        login()
        get_videos()
        choice = 'x'
        while(choice != 'Y' and choice != 'N' and choice != 'y' and choice != 'n'):
            choice = input("Do you want to create a json file to store the links? [Y/N]: ")
        if choice == 'Y' or choice == 'y':
            create_db()
        download_multiple(video_dict)
        pass
    #create_db()
    #download_all(video_dict)

    print("Download complete, thanks for flying with us!")
except Exception as e:
    print(e)
    sys.exit()
browser.close()
