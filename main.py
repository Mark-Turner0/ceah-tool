from helpers import getMacVer, getLinuxVer, getWindowsVer, getChromium, getFirefox, notify, onFail, getPath, getUAC, macLooper
from screens import wxFirstRun
from communicator import communicate
import socket
import platform
import os
import subprocess
import json
import asyncio
import psutil


def firstRun():
    try:
        f = open(getPath("DO_NOT_DELETE/id.txt"), 'r')
        unique = f.read()
        f.close()
        return unique
    except FileNotFoundError:
        return wxFirstRun()
    except Exception as e:
        onFail(e, critical=True)


def main():
    print("[OK]")
    unique = firstRun()
    data = {}
    print("Scanning OS...", end="\t\t")
    try:
        oper = platform.system().lower() if platform.system() != "Darwin" else "macos"
        data["os"] = oper
        print("[OK]")
    except Exception as e:
        onFail(e, critical=True)

    print("Getting OS version...", end='\t')
    try:
        if oper == "macos":
            osVer = subprocess.run(["sw_vers", "-buildVersion"], capture_output=True).stdout.decode()[:-1]
        elif oper == "windows":
            osVer = platform.platform()
        else:  # Linux
            osVer = os.uname()[2]
        data["osVer"] = osVer
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Checking privileges...", end='\t')
    try:
        if oper == "windows":
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                data["root"] = True
            else:
                data["root"] = False
        else:
            if not os.getuid():
                data["root"] = True
            else:
                data["root"] = False
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Scanning software...", end='\t')
    try:
        data["software"] = {}
        if oper == "macos":
            data["software"] = getMacVer(data["software"])
        elif oper == "windows":
            data["software"]["firefox"] = getFirefox()
            data["software"]["google chrome"] = getChromium()
            data["software"] = getWindowsVer(data["software"])
        else:
            data["software"] = getLinuxVer(data["software"])
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Getting firewall info...", end='')
    try:
        if oper == "macos":
            state = subprocess.run("/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate", capture_output=True, shell=True).stdout.decode()[:-1]
            if "enabled" in state:
                apps = subprocess.run("/usr/libexec/ApplicationFirewall/socketfilterfw --listapps", capture_output=True, shell=True).stdout.decode()[:-1]
                data["firewall_enabled"] = True
                data["firewall_rules"] = apps
            else:
                data["firewall_enabled"] = False
                data["firewall_rules"] = False
        elif oper == "windows":
            state = subprocess.run(["netsh", "advfirewall", "show", "currentprofile"], capture_output=True).stdout.decode()[:-1]
            if "OFF" in state:
                data["firewall_enabled"] = False
                data["firewall_rules"] = False
            else:
                data["firewall_enabled"] = True
                data["firewall_rules"] = state
        else:
            try:
                if not data["root"]:
                    raise FileNotFoundError
                state = subprocess.run(["ufw", "status", "verbose"], capture_output=True).stdout.decode()[:-1]
                if "inactive" in state:
                    data["firewall_enabled"] = False
                else:
                    data["firewall_enabled"] = True
                    data["firewall_rules"] = state
            except FileNotFoundError:
                data["firewall_enabled"] = "notdet"
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Testing internet...", end="\t")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname("captive.apple.com"), 80))
        s.send("GET / HTTP/1.1\r\nHost:captive.apple.com\r\n\r\n".encode())
        handshake = s.recv(4096).decode()
        if "Success" in handshake:
            internet = True
            data["ip_addr"] = s.getsockname()[0]
            print("[OK]")
        else:
            print("Connection error.")
    except Exception as e:
        internet = False
        onFail(e, critical=True)

    print("Testing antivirus...", end="\t")
    try:
        try:
            f = open("counter.txt", 'r')
            count = int(f.read())
            f.close()
        except FileNotFoundError:
            count = 6
        if count > 5:
            refresh = True
            count = 0
        else:
            refresh = False
        if refresh and internet:
            if oper == "windows":
                error_code = os.system("scripts\\antivirustestnew.bat")
            else:
                error_code = subprocess.run(["sh", getPath("scripts/antivirustestnew.sh")]).returncode
        elif not internet:
            print("[NO INTERNET]")
        else:
            if oper == "windows":
                error_code = os.system("scripts\\antivirustest.bat")
            else:
                error_code = subprocess.run(["sh", "scripts/antivirustest.sh"]).returncode

        if error_code == 9009 or error_code == 127:
            data["antivirus_scanning"] = "deleted / quarantined"
        elif error_code == 9020 or error_code == 126:
            data["antivirus_scanning"] = "caught on execution"
        elif error_code == 216 or error_code == 2:
            data["antivirus_scanning"] = "failed"
        else:
            data["antivirus_scanning"] = "unknown error " + str(error_code)
            raise Exception
        count += 1
        f = open("counter.txt", 'w')
        f.write(str(count))
        f.close()
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Checking access ctrls...", end='')
    try:

        if oper != "windows":
            username = os.environ.get("USER")
            adminCheck = subprocess.run(["id", "-G", username], capture_output=True).stdout.decode()[:-1]
            if "80 " in adminCheck:
                data["isAdmin"] = True
            else:
                data["isAdmin"] = False
            data["UAC"] = "unix"
        else:
            username = subprocess.run(["whoami"], capture_output=True).stdout.decode()[:-1]
            adminCheck = subprocess.run(["net", "user", username.split("\\")[-1]], capture_output=True).stdout.decode()[:-1]
            if "*Administrators" in adminCheck:
                data["isAdmin"] = True
            else:
                data["isAdmin"] = False
            data["UAC"] = getUAC()

        processes = {}
        for proc in psutil.process_iter():
            if oper == "windows" or proc.username() in [username, "root"]:
                try:
                    pusername = proc.username()
                    try:
                        if oper == "windows":
                            proc.memory_maps()
                        processes[proc.name()] = pusername
                    except psutil.AccessDenied:
                        if username.lower() not in pusername.lower():
                            raise psutil.AccessDenied
                        processes[proc.name()] = "UAC Elevated"
                except psutil.AccessDenied:
                    processes[proc.name()] = "Windows System"
        data["processes"] = processes
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Getting actions...", end='\t')
    try:
        f = open(getPath("notif.txt"))
        notif = [line.strip() for line in f]
        f.close()
        if notif == ["False"]:
            raise FileNotFoundError
        data["notification"] = notif
        print("[OK]")
    except FileNotFoundError:
        data["notification"] = False
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Saving data...", end='\t\t')
    try:
        f = open(getPath("data.json"), 'w')
        f.write(json.dumps(data, indent='\t'))
        f.close()
        print("[OK]")
    except Exception as e:
        onFail(e)

    communicate(unique)

    TOWAIT = 3000

    if oper == "macos":
        macLooper(TOWAIT)
    else:
        asyncio.get_event_loop().run_until_complete(notify(oper, TOWAIT))


if __name__ == '__main__':
    print("Importing libaries...", end='\t')
    while True:
        main()
