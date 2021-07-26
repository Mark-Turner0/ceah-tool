import os
import re
import sys
import subprocess
import random
import json
import asyncio
import webbrowser
import signal
import platform


def macLooper(toWait):

    def stop_loop():
        loop.stop()

    from external import _add_callback
    from rubicon.objc.eventloop import EventLoopPolicy
    from types import MethodType

    asyncio.set_event_loop_policy(EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop_loop)
    loop._add_callback = MethodType(_add_callback, loop)
    try:
        loop.run_until_complete(notify("macos", toWait))
    except RuntimeError:
        sys.exit(0)


def getPath(path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        if platform.system() == "Darwin" and not path.startswith("scripts/"):
            current = os.path.expanduser('~')
        else:
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
        if "positive" in ood:
            software = "positive"
        else:
            software = random.sample(ood.items(), 1)[0][0]
        f = open(getPath("notif.txt"), 'w')
        f.write(software)
        f.close()

        if software == "firewall_enabled":
            title = "ENABLE YOUR FIREWALL!"
            toShow = "Firewalls can help keep you safe!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "firewall_rules":
            title = "RECONFIGURE YOUR FIREWALL!"
            toShow = "A misconfigured firewall can be just as dangerous as not having one at all!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "antivirus_scanning":
            title = "TURN ON YOUR ANTIVIRUS!"
            toShow = "Antivirus can protect you"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "access controls":
            title = "CHECK YOUR ACCESS CONTROLS!"
            toShow = "Proper configuration can prevent bad things from happening!"
            if ood[software] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software]
        elif software == "osVer":
            title = "UPDATE " + oper.upper() + "!"
            toShow = oper.capitalize() + " updates can include important security patches"
            if ood[software][oper] != "":
                toShow += " Not sure how to do this? Click here!"
                url = ood[software][oper]
        elif software == "positive":
            title = "WELL DONE FOR UPDATING " + ood[software].upper() + "! 👍"
            toShow = "Up-to-date software is vital for cyber security!"

        else:
            title = "UPDATE " + software.upper()
            if ood[software] == "":
                f = open(getPath("data.json"), 'r')
                current = json.load(f)["software"][software]
                f = open(getPath("checked.json"))
                latest = json.load(f)["software"][software]
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
                command = 'defaults read "/Applications/' + i + '.app/Contents/Info" CFBundleShortVersionString'
                version = subprocess.check_output(command, shell=True).decode().strip()
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


def getUAC():
    command = "powershell.exe Get-ItemProperty -Path HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    results = subprocess.run(command.split(), capture_output=True).stdout.decode()[:-1].split("\r\n")[2:-10]
    uac = {}
    for i in results:
        keyValue = i.split(':')
        key = keyValue[0].replace(' ', "")
        value = keyValue[1][-1]
        uac[key] = value
    return uac
