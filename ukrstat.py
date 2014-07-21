# ukrstat.gov.ua crawling script

import requests
import time
import os
import zipfile
from bs4 import BeautifulSoup
from StringIO import StringIO

BASE_URL = "http://ukrstat.gov.ua/Noviny/"
BASE_DIR = "ukrstat"

# test script to check that links for each month are valid
"""
for i in ['%02d' % i for i in range(9,14)]:
    for j in ['%02d' % j for j in range(1,13)]:
        url = BASE_URL+"new20"+i+"/new20"+i+"_u/new_u"+j+".html"
        r = requests.get(url)
        time.sleep(1)
        if r.status_code == 200:
            print "Link for year", i, "and month", j, "is ok"
        else:
            print "Link for year", i, "and month", j, "is wrong"
"""
# all is ok, let's go to scraping

START_YEAR = 9 # in the current version of the site, there is no earlier 'news' than 2009
END_YEAR = 14 # change this to INCLUDE 2014 year in range

def main():
    """
    Downloads files from ukrstat.gov.ua, unpacking zip files and creating directories for each month in range
    """
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    for i in ['%02d' % i for i in range(START_YEAR,END_YEAR)]:
        for j in ['%02d' % j for j in range(1,13)]: # 1st to 12th months of the year
            url = BASE_URL+"new20"+i+"/new20"+i+"_u/new_u"+j+".html"
            r = requests.get(url)
            time.sleep(1) # to not overload ukrstat page
            fullpath = BASE_DIR+"/"+i+"/"+j+"/"
            if not os.path.exists(fullpath):
                os.makedirs(fullpath)
            soup = BeautifulSoup(r.text)
            links = [x.get('href') for x in soup.find_all('a')]
            oplinks = [link for link in links if link and link.find("operativ/operativ") != -1]
            oplinks = [link for link in oplinks if link.startswith('..')]
            newlinks = [link.replace('../../..', 'http://ukrstat.gov.ua') for link in oplinks]
            for link in newlinks:
                filename = link[31:].replace('/','_')
                page = requests.get(link)
                if page.status_code != 404:
                    if filename.endswith(".zip"):
                        z = zipfile.ZipFile(StringIO(page.content))
                        z.extractall(fullpath)
                        print "Unpacking zipped file", filename, "to the directory"
                    else:
                        with open(fullpath+filename, "w") as f:
                            f.write(page.content)
                            print "Writing file", filename, "to the directory"

            

def testmain():
    """
    Test script to use for only one month
    """
    testdirpath = 'test/'
    if not os.path.exists(testdirpath):
        os.mkdir(testdirpath)
    url = BASE_URL+"new2014/new2014_u/new_u04.html"
    r = requests.get(url)
    time.sleep(1) # to not overwhelm ukrstat.gov.ua
    fullpath = testdirpath
    if not os.path.exists(fullpath):
        os.mkdir(fullpath)
    soup = BeautifulSoup(r.text)
    links = [x.get('href') for x in soup.find_all('a')]
    oplinks = [link for link in links if link and link.find("operativ/operativ") != -1]
    oplinks = [link for link in oplinks if link.startswith('..')]
    newlinks = [link.replace('../../..', 'http://ukrstat.gov.ua') for link in oplinks]
    for link in newlinks:
        filename = link[31:].replace('/','_')
        page = requests.get(link)
        if page.status_code != 404:
            if filename.endswith(".zip"):
                z = zipfile.ZipFile(StringIO(page.content))
                z.extractall(testdirpath)
                print "Unpacking zipped file", filename, "to the directory"
            else:
                with open(testdirpath+filename, "w") as f:
                    f.write(page.content)
                    print "Writing file", filename, "to the directory"
        


if __name__ == "__main__":
    # change main() to testmain() to use test version of the script
    main()
