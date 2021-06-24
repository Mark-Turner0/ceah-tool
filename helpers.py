import os
import re

def getMacVer(path):
    f = open(path+"/Info.plist", 'r')
    content = f.read()
    f.close()
    return re.search("<key>CFBundleShortVersionString<\/key>\n\t<string>(.*)<",content).groups()[0]

def getChromium(path):
    if path.startswith("~"): #if os is linux
        path = path.replace('~',os.path.expanduser('~'))
        f = open(path,'r')
        content = f.read()
        f.close()
        return re.search('"last_chrome_version":"(.+?(?="))"',content).groups()[0]
    return os.listdir(path)[0]

def getBrave(path):
    if path.startswith("~"):
        path = path.replace('~',os.path.expanduser('~'))
        f = open(path,'r')
        content = f.read()
        f.close()
        return re.search('"last_chrome_version":"(.+?(?="))"',content).groups()[0]
    return os.listdir(path)[0]

def getFirefox(path):
    f = open(path,'r')
    content = f.read() 
    f.close()
    return re.search("Version=(.*)",content).groups()[0]
