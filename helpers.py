import os
import re
import subprocess

def getMacVer(appName):
    f = open("/Applications/"+appName+".app/Contents/Info.plist",'r')
    content = f.read()
    f.close()
    return re.search("<key>CFBundleShortVersionString<\/key>\n(.*)<string>(.*)<",content).groups()[1]

def getLinuxVer(installed):
    pkgmans = ["pacman","apt","dpkg"]
    for i in pkgmans:
        try:
            if i == "pacman": 
                results = subprocess.run("pacman -Q".split(' '), capture_output=True).stdout.decode()[:-1].split("\n")
                for j in results:
                    j = j.split()
                    installed[j[-2]] = j[-1]
            elif i == "apt":
                results = subprocess.run("apt list --installed".split(' '), capture_output=True).stdout.decode()[:-1].split("\n")
                for j in results:
                    name = j.split('/')[0]
                    version = j.split()[1]
                    installed[name] = version
            elif i == "dpkg":
                results = subprocess.run("dpkg -l".split(' '), capture_output=True).stdout.decode()[:-1].split("\n")
                for j in results:
                    j = j.split('\t')
                    installed[j[-2]] = j[-1]
        except FileNotFoundError:
            continue
    return installed


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
