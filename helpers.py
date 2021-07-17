import os
import re
import subprocess
import random
import json


def onFail(err_msg, critical=False, silent=False):
    if not silent:
        print("[FAIL]")
    try:
        f = open("errors.log", 'w')
        f.write(str(err_msg))
        f.close()
    except Exception:
        critical = True

    if critical:
        print("Critical Error! Exiting...")
        exit(0)


def urlCallback():
    import webbrowser
    webbrowser.open_new(url)


def notify(oper):
    PATHTOICON = "imgs/icon.png"
    global url
    url = "https://markturner.uk"
    f = open("notif.json", 'r')
    ood = json.load(f)
    software = random.sample(ood.items(), 1)[0][0]
    try:
        f = open("data.json", 'r')
        current = json.load(f)[software]
        f = open("checked.json")
        latest = json.load(f)[software]
        f.close()
        if ood[software] == "":
            toShow = "from version " + current + " to version " + latest
        else:
            toShow = "Not sure how to do this? Click here!"
            url = ood[software]
        if oper == "macos":
            import pync
            pync.notify(toShow, title="UPDATE " + software.upper() + "!", open=url, appIcon=PATHTOICON)
        elif oper == "windows":
            from win10toast_click import ToastNotifier
            ToastNotifier().show_toast("UPDATE " + software.upper(), toShow, callback_on_click=urlCallback)
        else:
            os.system("notify-send 'UPDATE " + software.upper() + "' '" + toShow + "'")
    except KeyError:
        print("Nothing to notify.")


def getMacVer(installed):
    for i in os.listdir("/Applications/"):
        try:
            if i.endswith(".app"):
                i = i[:-4]
                f = open("/Applications/" + i + ".app/Contents/Info.plist", 'r')
                content = f.read()
                f.close()
                version = re.search("<key>CFBundleShortVersionString</key>\n(.*)<string>(.*)<", content).groups()[1]
                installed[i.lower()] = version
        except Exception:
            installed[i.lower()] = False
    return installed


def getLinuxVer(installed):
    pkgmans = ["pacman", "apt", "dpkg"]
    for i in pkgmans:
        try:
            if i == "pacman":
                results = subprocess.run("pacman -Q".split(), capture_output=True).stdout.decode()[:-1].split("\n")
                for j in results:
                    j = j.split()
                    installed[j[-2].lower()] = j[-1]
            elif i == "dpkg":
                results = subprocess.run("dpkg -l".split(), capture_output=True).stdout.decode()[:-1].split("\n")[5:]
                for j in results:
                    j = j.split()
                    installed[j[1].lower()] = j[2]
            elif i == "apt":
                results = subprocess.run("apt list --installed".split(), capture_output=True).stdout.decode()[:-1].split("\n")[1:]
                for j in results:
                    name = j.split('/')[0]
                    version = j.split()[1]
                    installed[name.lower()] = version
        except FileNotFoundError:
            continue
    return installed


def getWindowsVer(installed):
    commands = ["""
                powershell.exe Get-ItemProperty
                HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
                Format-List -Property DisplayName, DisplayVersion""",

                """powershell.exe Get-ItemProperty
                HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
                Format-List -Property DisplayName, DisplayVersion"""]

    for command in commands:
        results = subprocess.run(command.split(), capture_output=True).stdout.decode()[:-1].split("\r\n\r\n")[1:-1]
        for i in results:
            i = i.split("\r\n")
            try:
                name = i[0].split(": ")[-1]
                if name != "":
                    version = i[1].split(": ")[-1]
                    installed[name.lower()] = version
            except IndexError:
                pass
    return installed


def getChromium():
    path = "C:\\Program Files (x86)\\Google\\Chrome\\Application"
    return os.listdir(path)[0]


def getFirefox():
    path = "C:\\Program Files\\Mozilla Firefox\\application.ini"
    f = open(path, 'r')
    content = f.read()
    f.close()
    return re.search("Version=(.*)", content).groups()[0]
