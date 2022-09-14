# MoodleScraper
## Download chromedriver
Chromedriver can be manually downloaded (see curl-based download below) at https://chromedriver.chromium.org/downloads.

Manually downloaded binaries must be place in the `bin` directory with correct naming: `chromedriver_LINUX64` for Linux, `chromedriver_MAC64` for Mac, `chromedriver_MAC_M1` for Mac M1 and `chromedriver_WIN32.exe` for Windows.

In order to use Chromedriver you must have Chrome installed on default system location.

### MacOS

Download and extract chromedriver 106 in bin folder with correct name, then make it executable:

#### MAC64

    curl -O https://chromedriver.storage.googleapis.com/106.0.5249.21/chromedriver_mac64.zip
    unzip chromedriver_mac64.zip
    mv chromedriver bin/chromedriver_MAC64
    rm chromedriver_mac64.zip
    chmod +x bin/chromedriver_MAC64

#### MAC M1

    curl -O https://chromedriver.storage.googleapis.com/106.0.5249.21/chromedriver_mac64_m1.zip
    unzip chromedriver_mac64_m1.zip
    mv chromedriver bin/chromedriver_MAC_M1
    rm chromedriver_mac64_m1.zip
    chmod +x bin/chromedriver_MAC_M1

If you're using macOS go to Macintosh HD > Applications > Python3.9 folder (or whatever version of python you're using) > double click on "Install Certificates.command" file.

### Linux

Download and extract chromedriver 106 in bin folder with correct name, then make it executable:

    curl -O https://chromedriver.storage.googleapis.com/106.0.5249.21/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    mv chromedriver bin/chromedriver_LINUX64
    rm chromedriver_linux64.zip
    chmod +x bin/chromedriver_LINUX64

### Windows

Nobody want to do scripting with Windows, do it yourself or manually download and rename the binary.

## Install python dependencies

    pip3 install -r requirements.txt

## Usage
```
python MoodleScraper.py [-v] course_page_link
```
or
```
python MoodleScraper.py [-v] -j json_file_name_WO_extension
```
verbose mode can be enabled using:
```
-v
```
For help:
```
python MoodleScraper.py [-h]
```