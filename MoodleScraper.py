from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import urllib.request
import os
from pathlib import Path
import sys
import time
import argparse
from getpass import getpass
import platform
import json
from inputimeout import inputimeout, TimeoutOccurred


def hello():
    print('''
███╗   ███╗ ██████╗  ██████╗ ██████╗ ██╗     ███████╗    ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
████╗ ████║██╔═══██╗██╔═══██╗██╔══██╗██║     ██╔════╝    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██╔████╔██║██║   ██║██║   ██║██║  ██║██║     █████╗      ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
██║╚██╔╝██║██║   ██║██║   ██║██║  ██║██║     ██╔══╝      ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██████╔╝███████╗███████╗    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝                                                                                                                        
    ''')  

def validateInput():
    global JSONFILE
    global COURSEPAGE
    if(fromJson==None):
        if(COURSEPAGE==""):     #if not '-j' swap first (if not void) arg with second (jsonFile with Coursepage)
            if(JSONFILE!=""):
                COURSEPAGE=JSONFILE
            else:               #if first argument is void
                print("ERR: Invalid Arguments! You must specify at least a Course Page or a JSON file (along with [-j] option)")
                print(parser.format_help())
                sys.exit()
    elif(fromJson[0]==1):
        if(JSONFILE==""):       #if 'j' swap second (if not void) arg with first (Coursepage with jsonFile)
            if(COURSEPAGE!=""):
                JSONFILE=COURSEPAGE
            else:               #if first argument is void
                print("ERR: Invalid Arguments! You must specify at least a Course Page or a JSON file (along with [-j] option)")
                print(parser.format_help())
                sys.exit()     

parser = argparse.ArgumentParser(description="Download all Kaltura videos from a UniTN Moodle page.")
parser.add_argument('-v', '--verbose' ,help="verbose", required=False, action='append_const', const=1)
parser.add_argument('-j', '--json' ,help="download from existing json", required=False, action='append_const', const=1)
parser.add_argument("jsonFile",help="JSON File Name without extension (must be in 'json' folder)",type=str, default="",nargs='?')
parser.add_argument("Page_URL",help="Moodle Page link",type=str, nargs='?', default="")
args=parser.parse_args()
verbose=args.verbose
fromJson=args.json
JSONFILE=args.jsonFile
COURSEPAGE=args.Page_URL
validateInput()
hello()

USERNAME = ""
PASSWORD = ""
LOGINPAGE="https://didatticaonline.unitn.it/dol/loginUniTN.php"
opsys=platform.system()


def selWait(by,value,time=3):
    wait=WebDriverWait(browser,time)
    try:
        wait.until(EC.presence_of_element_located((by,value)))
    except Exception as e:
        print(e)

def waitAndFind(by,value):
    selWait(by,value)
    return browser.find_element(by, value=value)

def waitAndFindMultiple(by,value):
    selWait(by,value)
    return browser.find_elements(by, value=value)

def validList(list,maxn):   #input is valid if is "all" or numbers in range ( [1:lastVideoIndex] ) separed by a comma
    valid=1
    for number in list:
        if(number=="all" and len(list)==1):
            return valid
        if(not number.isnumeric()):
            return 0
        if(int(number)<1):
            return 0
        if(int(number)>maxn):
            return 0
    return valid

def write_json(filename, jsonObj):
    filename=filename.replace("/", "-")
    filename=filename.replace(" ", "_")
    path=os.path.join("json", filename+'.json')
    try:
        with open(path, 'w') as outfile:
            json.dump(jsonObj, outfile, indent=2)
    except Exception as e:
        print(e)

def create_db():
    json_filename = coursename
    write_json(json_filename, video_dict)

def json2dict(filename):
    path=os.path.join("json", str(filename))
    with open(path, "r") as read_file:
        try:
            dict = json.load(read_file)
        except Exception as e:
            print("json not valid!")
            print(e)
            sys.exit()
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
    in_list="-1"
    maxtime=25
    while(not validList(list(in_list.split(',')),len(dict))):
        try:
            in_list=inputimeout(prompt="('all' in " + str(int(maxtime)) + "s): ", timeout=maxtime)
        except TimeoutOccurred:
            sys.stdout.flush()
            in_list ="all"
            print("all")
        sys.stdout.flush()
    if(in_list != 'all'):
        in_list = list(in_list.split(','))
        for video in in_list:
            index=int(video)-1  #list start from 1 and not from 0
            try:
                print(f"Downloading: {list(dict.keys())[index]}")
                download_single_video(list(dict.keys())[index])
                print("")
            except Exception as e:
                print(e)
    else:
        download_all(dict)

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

def download_single_video(obj):
    p=os.path.join("Videos/",coursename)
    path=Path(p)
    path.mkdir(parents=True, exist_ok=True)
    global video_dict
    global start_time
    #download video from source page
    filename=obj.replace("/", "-")
    path=os.path.join(p, filename+".mp4")
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
    global USERNAME
    global PASSWORD
    USERNAME=input("Enter username: ")
    PASSWORD=getpass()
    print("Logging in...")
    #get login page
    browser.get(LOGINPAGE)
    LOGINP=waitAndFind(By.ID,"btn-login-unitn-it")
    LOGINP.click()

    #login page
    username = waitAndFind(By.NAME,"j_username")
    username.send_keys(USERNAME)

    password = waitAndFind(By.NAME,"j_password")
    password.send_keys(PASSWORD)

    accedi = waitAndFind(By.ID,"btnAccedi")
    pagina=browser.current_url
    accedi.click()
    if(pagina[0:-4]==browser.current_url[0:-4]):
        print("ERROR: Wrong username or password!")
        login()

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

    if(len(videos)>0):
        print("Found " + str(len(videos))+ " videos...")
        print("The script will browse through every video to create a download link, it may take a while")
        print("Creating download list...")
    else:
        print("No video found!")
        print("Closing all browser instances, please wait...")
        browser.quit()
        print("See you soon!")
        sys.exit()
        

    video_dict = {}
    i=1
    for key in videos :
        #go to video page
        browser.get(videos[key])

        #get video link
        print(f"Getting video link #{i} of {len(videos)}")
        try:
            selWait(By.ID, "contentframe",2)
            browser.switch_to.frame("contentframe")
            selWait(By.ID, "kplayer_ifp",2)
            browser.switch_to.frame("kplayer_ifp")
        except Exception as e:
            print("W: One ore more frames not found, please wait...")
        try:
            linkElem = waitAndFind(By.ID,"pid_kplayer")
            link=linkElem.get_attribute("src")
        except Exception as e:
            print("W: pid_kplayer not found, please wait...")
            print(e)
            browser.switch_to.default_content()
            link=waitAndFind(By.XPATH,'//*[@id="contentframe"]').get_attribute('src')
        
        video_dict[key] = link
        i+=1


#set driver
def main():
    global coursename
    global video_dict
    global browser
    global fromJson
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if(verbose==None):
            options.headless = True
        if(opsys=="Windows"):
            ser=Service(os.path.join("bin","chromedriver_WIN32.exe"))
            browser = webdriver.Chrome(options=options, service=ser)
        elif(opsys=="Linux"):
            ser=Service(os.path.join("bin","chromedriver_LINUX64"))
            browser = webdriver.Chrome(options=options,service=ser)
        elif(opsys=="Darwin"):
            if(platform.architecture=="arm"):
                ser=Service(os.path.join("bin","chromedriver_MAC_M1"))
                browser = webdriver.Chrome(options=options,service=ser)
            else:
                ser=Service(os.path.join("bin","chromedriver_MAC64"))
                browser = webdriver.Chrome(options=options,service=ser)
    except Exception as e :
        print(e)
        sys.exit()
    if(verbose==None):
        print("Starting Chrome silently...")
    else:
        print("Starting Chrome...")
    try:
        if(fromJson!=None):
            jsonPath=os.path.join("json", JSONFILE+".json")
            if(os.path.isfile(jsonPath)):
                coursename=JSONFILE
                #login()
                video_dict=json2dict(JSONFILE+".json")
                download_multiple(video_dict)
            else:
                print("ERR: JSON file doesn't exist!")
                sys.exit()
        else:        
            login()
            get_videos()
            choice = 'x'
            maxtime=10
            while(choice != 'Y' and choice != 'N' and choice != 'y' and choice != 'n'):
                message="Do you want to create a json file to store the links? [Y/N]:"
                print(message)
                try:
                    choice = inputimeout(prompt="('Y' in " + str(int(maxtime)) + "s): ", timeout=maxtime)
                except TimeoutOccurred:
                    sys.stdout.flush()
                    choice ='Y'
                    print("Y")
            if choice == 'Y' or choice == 'y':
                p=os.path.join("json")
                path=Path(p)
                path.mkdir(parents=True, exist_ok=True)
                create_db()
            download_multiple(video_dict)
            #create_db()
            #download_all(video_dict)
        print("Download complete, thanks for flying with us!")
    except KeyboardInterrupt:
        print("")
        print("Moodle Scraper terminated by user!")
        print("Closing all browser instances, please wait...")
        browser.quit()
        print("See you soon!")
        sys.exit()
    except Exception as e:
        print(e)
        browser.quit()
        sys.exit()
    browser.quit()


if __name__ == "__main__":
    main()
