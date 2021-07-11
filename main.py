from helpers import getMacVer, getLinuxVer, getWindowsVer, getChromium, getFirefox, notify, onFail
from communicator import communicate
import socket
import platform
import os
import subprocess
import json
import random
import time


def firstRun():
    try:
        f = open("DO_NOT_DELETE/id.txt", 'r')
        unique = f.read()
        f.close()
        return unique, False
    except FileNotFoundError:
        print("First run mode enabled.")
        unique = ""
        for i in range(7):
            if random.randint(0, 1):
                unique += chr(random.randint(97, 122))
            else:
                unique += chr(random.randint(48, 57))
        os.mkdir("DO_NOT_DELETE")
        f = open("DO_NOT_DELETE/id.txt", 'w')
        f.write(unique)
        f.close()
        return unique, True
    except Exception as e:
        onFail(e, critical=True)


def main():
    print("[OK]")
    unique, is_first = firstRun()
    installed = {}
    print("Scanning OS...", end="\t\t")
    try:
        oper = platform.system().lower() if platform.system() != "Darwin" else "macos"
        installed["os"] = oper
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
        installed["osVer"] = osVer
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Getting IP address...", end='\t')
    try:
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname_ex(hostname)[2]
        for i in ip_addr:
            if i[:4] != "127.":
                installed["ip_addr"] = i
                break
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Scanning software...", end='\t')
    try:
        if oper == "macos":
            installed = getMacVer(installed)
        elif oper == "windows":
            installed["Firefox"] = getFirefox()
            installed["Chrome"] = getChromium()
            installed = getWindowsVer(installed)
        else:
            installed = getLinuxVer(installed)
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Getting firewall info...", end='')
    try:
        if oper == "macos":
            state = subprocess.run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"], capture_output=True).stdout.decode()[:-1]
            if "enabled" in state:
                apps = subprocess.run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--listapps"], capture_output=True).stdout.decode()[:-1]
                installed["firewall_enabled"] = True
                installed["firewall_rules"] = apps
            else:
                installed["firewall_enabled"] = False
        else:
            state = subprocess.run(["ufw", "status", "verbose"], capture_output=True).stdout.decode()[:-1]
            if "inactive" in state:
                installed["firewall_enabled"] = False
            else:
                installed["firewall_enabled"] = True
                installed["firewall_rules"] = state
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
            print("[OK]")
        else:
            print("Connection error.")
    except Exception as e:
        internet = False
        onFail(e, critical=True)

    try:
        print("Testing antivirus...", end="\t")
        if is_first and internet:
            if oper == "windows":
                error_code = os.system("scripts\\antivirustestnew.bat")
            else:
                error_code = subprocess.run(["sh", "scripts/antivirustestnew.sh"]).returncode
        elif not internet:
            print("[NO INTERNET]")
        else:
            if oper == "windows":
                error_code = os.system("scripts\\antivirustest.bat")
            else:
                error_code = subprocess.run(["sh", "scripts/antivirustest.sh"]).returncode

        if error_code == 9009 or error_code == 127:
            installed["antivirus scanning"] = "deleted / quarantined"
        elif error_code == 9020 or error_code == 126:
            installed["antivirus scanning"] = "caught on execution"
        elif error_code == 216 or error_code == 2:
            installed["antivirus scanning"] = "failed"
        else:
            installed["antivirus scanning"] = "unknown error " + str(error_code)
            raise Exception
        print("[OK]")
    except Exception as e:
        onFail(e)

    print("Saving data...", end='\t\t')
    try:
        f = open("data.json", 'w')
        f.write(json.dumps(installed, indent='\t'))
        f.close()
        print("[OK]")
    except Exception as e:
        onFail(e)

    while True:
        communicate(unique)
        notify(oper)
        time.sleep(600)


if __name__ == '__main__':
    print("Importing libaries...", end='\t')
    main()
