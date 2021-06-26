import os
import re
import subprocess

def getMacVer():
    for i in os.listdir("/Applications/"):
        try:
            if i.endswith(".app"):
                i = i[:-4]
                f = open("/Applications/"+i+".app/Contents/Info.plist",'r')
                f.close()
                version = re.search("<key>CFBundleShortVersionString<\/key>\n(.*)<string>(.*)<",content).groups()[1]
                installed[i] = version
        except:
            installed[i] = False
    return installed 

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

def getWindowsVer(installed):
    commands = ["powershell.exe Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Format-List -Property DisplayName, DisplayVersion",
            "powershell.exe Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Format-List -Property DisplayName, DisplayVersion"]
    for command in commands:
        results = subprocess.run(command.split(), capture_output=True).stdout.decode()[:-1].split("\r\n\r\n")[1:-1]
        for i in results:
            i = i.split("\r\n")
            try:
                name = i[0].split(": ")[-1]
                if name != "":
                    version = i[1].split(": ")[-1]
                    installed[name] = version
            except IndexError:
                pass
    return installed


def getChromium():
    path = "C:\\Program Files (x86)\\Google\\Chrome\\Application"
    return os.listdir(path)[0]


def getFirefox():
    path = "C:\\Program Files\\Mozilla Firefox\\application.ini" 
    f = open(path,'r')
    content = f.read() 
    f.close()
    return re.search("Version=(.*)",content).groups()[0]
