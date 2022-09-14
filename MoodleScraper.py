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
import socket
from inputimeout import inputimeout, TimeoutOccurred
import shutil
import pathvalidate
from contextlib import suppress
import psutil


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

def exitRoutine():
    print("Closing all browser instances, please wait...")
    browser.stop_client()
    browser.quit()
    #assert that all processes are terminated (on windows it's the only way to properly close chromedriver from an exception)
    #TODO:check for other OS if it's closing
    if(opsys=="Windows"):
        for process in psutil.process_iter():
            if process.name() == 'chrome.exe' and '--test-type=webdriver' in process.cmdline():
                with suppress(psutil.NoSuchProcess):
                    p = psutil.Process(process.pid)
                    p.terminate()
    print("See you soon!")
    sys.exit()

def isConnected():
    try:
        # connect to the host -- tells us if the host is actually reachable
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            sock.close
        return True
    except OSError:
        pass
    return False

def checkConnection():
    global browser
    if(not isConnected()):
        print("Connection lost, please wait...")
        i=0
        for i in range(0,5):
            print("Reconnecting, attempt #" + str(i+1) +"...")
            time.sleep(2)
            if(isConnected()):
                print("Reconnected!")
                break
        if(i==4):
            print("No connection, retry later!") 
            exitRoutine()

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
        if(number=="all" and len(list)>0):  #if input is 'all' skip all cicle and return
            return valid
        if(not number.isnumeric()):
            return 0
        if(int(number)<1):
            return 0
        if(int(number)>maxn):
            return 0
    return valid

def write_json(filename, jsonObj):
    filename=pathvalidate.sanitize_filename(filename)
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
            if(len(dict)<2):
                raise Exception("json is empty!")
        except Exception as e:
            print("json not valid!")
            print(e)
            exitRoutine()
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
    in_list=""
    maxtime=25
    firstIt=1
    while(not validList(list(in_list.split(',')),len(dict))):
        if(firstIt!=1):
            print("Input invalid!")
        try:
            in_list=inputimeout(prompt="('all' in " + str(int(maxtime)) + "s): ", timeout=maxtime)
            firstIt=0
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
    p=os.path.join("Videos/",coursename+"_videos")
    path=Path(p)
    path.mkdir(parents=True, exist_ok=True)
    global video_dict
    global start_time
    #download video from source page
    filename=pathvalidate.sanitize_filename(obj)
    filename=filename.replace(" ","_")
    filename=str(obj)+'-'+filename
    print(filename)
    path=os.path.join(p, filename+".mp4")
    start_time=time.time()
    urllib.request.urlretrieve(video_dict[obj], path, reporthook)

#download all videos
def download_all(dict):
    i = 0
    for j in dict:
        download_single_video(j)
        print("\n"+"Video "+ str(i+1)+" of " + str(len(dict)) + " downloaded please wait...")
        i=i+1

def download_wait():
    directory=os.path.join(os.getcwd(),"Files","temp", "")
    seconds = 0
    dl_wait = True
    while dl_wait:
        fileProgress(seconds,"Downloading files, please wait")
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    return seconds

def moveFiles():
    global coursename
    source_folder = os.path.join(os.getcwd(),"Files","temp", "")
    destination_folder = os.path.join(os.getcwd(),"Files",coursename+"_files", "")

    print("Moving files, plese wait...")
    # fetch all files
    for file_name in os.listdir(source_folder):
        # construct full file path
        source = source_folder + file_name
        destination = destination_folder + file_name
        shutil.move(source, destination)
    shutil.rmtree(os.path.join(os.getcwd(),"Files","temp"))

def fileProgress(i,stringa):
    dots=i%4
    stringa
    while(dots>0):
        stringa=stringa + "."
        dots=dots-1
    print("\r {}".format(stringa+"   "), end="")

def download_files():
    global coursename
    global video_dict
    global start_time

    p2=os.path.join("Files","temp")
    path2=Path(p2)
    path2.mkdir(parents=True, exist_ok=True)
    #get course page
    browser.get(COURSEPAGE)

    coursename=waitAndFind(By.TAG_NAME,"h1").text
    coursename=pathvalidate.sanitize_filename(coursename)
    coursename=coursename.replace(" ", "_")
    p=os.path.join("Files",coursename +"_files")
    path=Path(p)
    path.mkdir(parents=True, exist_ok=True)

    print("Searching for files...")
    topics=waitAndFindMultiple(By.CLASS_NAME,"aalink")

    index=0
    files={}
    folders={}
    for topic in topics:
        if ("File" in topic.text or "Cartella" in topic.text):
            filename_list=topic.text.split("\n",1)
            filename=filename_list[0]
            filename=pathvalidate.sanitize_filename(filename)
            filename=filename.replace(" ", "_")
            filename=str(index)+'-'+filename
            print(filename)
            filetype=filename_list[1]
            if(filetype=="File"):
                files[topic.get_attribute("href")]=filename
            elif(filetype=="Cartella"):
                folders[topic.get_attribute("href")]=filename
            index+=1
    print()

    if((len(files)+len(folders))>0):
        print("Found " + str((len(files)+len(folders)))+ " files...")
        print("The script will download them all, it may take a while")
    else:
        print("No files found!")

    fileURLS=[]
    i=0
    for file in files:
        #download files
        path2=os.path.join(p2, files[file])

        #execute javascript code that obtain the redirection url
        #jsCode= "var xhr = new XMLHttpRequest();" + "xhr.open('GET', arguments[0], false);" + "xhr.send(null);" + "return xhr.responseURL;"
        #fileURL= browser.execute_script(jsCode,files[file])

        #simpler solution
        fileURL=file+"&redirect=1"

        #remove forcedownload=1 from url in order to get file resource url
        if("forcedownload=1" in fileURL):
            fileURL=fileURL.replace("?forcedownload=1","")

        fileURLS.append(fileURL)
        fileProgress(i,"Creating file list")
        i=i+1


    for folder in folders:
        #download folders
        path2=os.path.join(p2, folders[folder])
        url=folder
        browser.get(url)
        waitAndFind(By.XPATH, value="//button[@type='submit' and @class='btn btn-secondary']").click()
        download_wait()
        i=i+1


    for file in fileURLS:
        browser.get(file)
        if("mp4" in browser.current_url):
            browser.execute_script("window.location = \'"+browser.current_url+"?forcedownload=1"+"\';" "window.stop;")  #necessary to navigate to page with js script in order to stop loading the page, otherwise chromedriver get stuck in that page
        download_wait()
        i=i+1

    time.sleep(2)
    print("")
    moveFiles()
    print("Files download complete!")


def login():
    global USERNAME
    global PASSWORD
    USERNAME=input("Enter username: ")
    PASSWORD=getpass()
    print("Logging in...")
    #get login page
    browser.get(LOGINPAGE)
    LOGINP=waitAndFind(By.ID,"btn-login-unitn-en")   #TODO: make it independent of the system language
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
    coursename=pathvalidate.sanitize_filename(coursename)
    coursename=coursename.replace(" ","_")
    topics = waitAndFindMultiple(By.CLASS_NAME,"aalink")

    print("Searching for Kaltura videos...")

    videos = {}
    for topic in topics:
        name=''
        if "Kaltura Video Resource" in topic.text:
            name=topic.text.replace("Kaltura Video Resource","")    #remove useless chars
            name=name[0:-1]                                         #remove \n
            videos[name]=topic.get_attribute("href")
        elif "Kaltura Video Presentation" in topic.text:
            name2=topic.text.replace("Kaltura Video Presentation","")   #remove useless chars
            name2=name2[0:-1]                                           #remove \n
            videos[name2]=topic.get_attribute("href")
        if(name!=''):
            print(name)
    print()

    if(len(videos)>0):
        print("Found " + str(len(videos))+ " videos...")
        print("The script will browse through every video to create a download link, it may take a while")
        print("Creating download list...")
    else:
        print("No video found!")
        exitRoutine()
        

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
        except Exception:
            print("W: One ore more frames are hidden, please wait...")
        try:
            linkElem = waitAndFind(By.ID,"pid_kplayer")
            link=linkElem.get_attribute("src")
        except Exception:
            print("W: pid_kplayer is hidden, please wait...")
            waitAndFind(By.TAG_NAME,"button").click()
            name=waitAndFind(By.XPATH, "//*[contains(@id, 'kaltura_player')]")
            name=name.get_attribute("id")
            browser.switch_to.frame(name+"_ifp")
            linkElem=waitAndFind(By.ID,"pid_"+name)
            link=linkElem.get_attribute("src")

        video_dict[key] = link
        i+=1

def main():
    global coursename
    global video_dict
    global browser
    global fromJson
    try:    #first try-catch in case of non instanced browser
        #set driver
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('prefs', {
        "download.default_directory": os.path.join(os.getcwd(),"Files","temp"), #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
        })
        options.add_argument("--mute-audio")
        options.add_argument("--window-size=500,500")
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
    except KeyboardInterrupt:
        print("Moodle Scraper terminated by user!")
        print("See you soon!")
        sys.exit()
    except Exception as e :
        print(e)
        sys.exit()
    if(verbose==None):
        print("Starting Chrome silently...")
    else:
        print("Starting Chrome...")
    try:    #second try-catch in case of instanced browser
        checkConnection()
        if(fromJson!=None):
            jsonPath=os.path.join("json", JSONFILE+".json")
            if(os.path.isfile(jsonPath)):
                coursename=JSONFILE
                #login()
                video_dict=json2dict(JSONFILE+".json")
                checkConnection()
                download_multiple(video_dict)
            else:
                print("ERR: JSON file doesn't exist!")
                exitRoutine()
        else:
            checkConnection()   
            login()
            choice = 'x'
            maxtime=10
            while(choice != 'Y' and choice != 'N' and choice != 'y' and choice != 'n'):
                message="Do you want to download files? [Y/N]:"
                print(message)
                try:
                    choice = inputimeout(prompt="('Y' in " + str(int(maxtime)) + "s): ", timeout=maxtime)
                except TimeoutOccurred:
                    sys.stdout.flush()
                    choice ='Y'
                    print("Y")
            print("Ok!")
            if choice == 'Y' or choice == 'y':
                download_files()

            global video
            video=False
            choice = 'x'
            maxtime=10
            while(choice != 'Y' and choice != 'N' and choice != 'y' and choice != 'n'):
                message="Do you want to download Kaltura videos? [Y/N]:"
                print(message)
                try:
                    choice = inputimeout(prompt="('Y' in " + str(int(maxtime)) + "s): ", timeout=maxtime)
                except TimeoutOccurred:
                    sys.stdout.flush()
                    choice ='Y'
                    print("Y")
            print("Ok!")
            if choice == 'Y' or choice == 'y':
                get_videos()
                video=True
            
            if(video==True):
                choice = 'x'
                maxtime=10
                while(choice != 'Y' and choice != 'N' and choice != 'y' and choice != 'n'):
                    message="Do you want to create a json file to store the video links? [Y/N]:"
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
        exitRoutine()
    except Exception as e:
        print(e)
        browser.stop_client()
        browser.quit()
        sys.exit()
    browser.quit()
    sys.exit()

if __name__ == "__main__":
    main()
