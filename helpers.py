import os
import re
import sys
import subprocess
import random
import json
import asyncio
import webbrowser


def getPath(path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        current = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(current, path)
    return path


def onFail(err_msg, critical=False, silent=False):
    if not silent:
        print("[FAIL]")
    try:
        f = open(getPath("errors.log"), 'w')
        f.write(str(err_msg))
        f.close()
    except Exception:
        critical = True

    if critical:
        print("Critical Error! Exiting...")
        sys.exit(0)


def dismissedCallback():
    f = open(getPath("notif.txt"), 'a')
    f.write("\ndismissed")
    f.close()


def clickCallback():
    f = open(getPath("notif.txt"), 'a')
    f.write("\nclicked")
    f.close()
    webbrowser.open_new(url)


async def notify(oper, toWait):
    global url
    url = "https://markturner.uk"
    f = open(getPath("notif.json"), 'r')
    ood = json.load(f)
    f.close()
    try:
        software = random.sample(ood.items(), 1)[0][0]

        if software == "firewall":
            title = "ENABLE YOUR FIREWALL!"
            toShow = "Firewalls can help keep you safe!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "firewall_incorrect":
            title = "RECONFIGURE YOUR FIREWALL!"
            toShow = "A misconfigured firewall can be just as dangerous as not having one at all!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "antivirus":
            title = "TURN ON YOUR ANTIVIRUS"
            toShow = "Antivirus can protect you!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "access controls":
            title = "CHECK YOUR ACCESS CONTROLS!"
            toShow = "Proper configuration can prevent bad things from happening!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]

        else:
            title = "UPDATE " + software.upper()
            f = open(getPath("notif.txt"), 'w')
            f.write(software)
            f.close()
            if ood[software] == "":
                f = open(getPath("data.json"), 'r')
                current = json.load(f)[software]
                f = open(getPath("checked.json"))
                latest = json.load(f)[software]
                f.close()
                toShow = "from version " + current + " to version " + latest
            else:
                toShow = "Not sure how to do this? Click here!"
                url = ood[software]
        if oper != "windows":
            from desktop_notifier import DesktopNotifier
            notify = DesktopNotifier(app_name="Cyber Essentials at Home", app_icon=getPath("imgs/logo.ico"))
            await notify.send(title=title, message=toShow, on_clicked=lambda: clickCallback(), on_dismissed=lambda: dismissedCallback())
        else:
            from win10toast_click import ToastNotifier
            ToastNotifier().show_toast(title, toShow, icon_path="imgs\\logo.ico", callback_on_click=clickCallback)
    except ValueError:
        print("Nothing to notify.")
        f = open(getPath("notif.txt"), 'w')
        f.write("False")
        f.close()
    except Exception as e:
        onFail(e)
    print("Sleeping...", end='\t\t')
    await asyncio.sleep(toWait)


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
