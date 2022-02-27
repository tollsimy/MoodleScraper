# MoodleScraper
## Installation
Chromedriver can be downloaded https://chromedriver.chromium.org/downloads and i don't own any part of it.<br />
In order to use Chromedriver you must have Chrome installed on default location.

### MacOS
If you're using macOS go to Macintosh HD > Applications > Python3.9 folder (or whatever version of python you're using) > double click on "Install Certificates.command" file.

In case of error with chromedriver_* please give permission to the program using

    chmod +x chromedriver_*
Where * can be _MAC_M1_ for Mac with arm processor and _MAC64_ for the intel ones.

### Linux
In case of error with chromedriver_LINUX64 please give permission to the program using

    chmod +x chromedriver_LINUX64

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