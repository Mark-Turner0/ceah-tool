from helpers import *
import socket
import platform
import os
import subprocess
import json
import random

def onFail(critical=False):
	print("[FAIL]")
	if critical: 
		print("Critical Error! Exiting...")
		exit(0)

def firstRun():
    try:
        f = open("DO_NOT_DELETE/id.txt",'r')
        unique = f.read()
        f.close()
        return unique
    except FileNotFoundError:
        print("First run mode enabled.")
        unique = ""
        for i in range(7):
            if random.randint(0,1):
                unique += chr(random.randint(97,122))
            else:
                unique += chr(random.randint(48,57))
        os.mkdir("DO_NOT_DELETE")
        f = open("DO_NOT_DELETE/id.txt",'w')
        f.write(unique)
        f.close()
        return unique
    except:
        onFail(True)

def main():
    print("[OK]")
    unique = firstRun()
    installed = {}
    print("Scanning OS...",end="\t")
    try:
        oper = platform.system().lower() if platform.system() != "Darwin" else "macos"
        installed["os"] = oper
        print("[OK]")
    except:
        onFail(True)

    print("Getting OS version...",end='\t')
    try:
        if oper == "macos":
            osVer = subprocess.run(["sw_vers","-buildVersion"], capture_output=True).stdout.decode()[:-1]
        elif oper == "windows":
            osVer = platform.platform()
        else: #Linux
            osVer = os.uname()[2]
        installed["osVer"] = osVer
        print("[OK]")
    except:
        onFail()

    print("Scanning software...",end='\t')
   # try:
    f = open("paths.json",'r')
    software = f.read()
    f.close()
    software = json.loads(software)

    if oper == "macos":
        for i in os.listdir("/Applications/"):
            try:
                if i.endswith(".app"):
                    i = i[:-4]
                    installed[i] = getMacVer(i)
            except:
                installed[i] = False
    elif oper == "windows":       
        for i in software.keys():
            try:
                if i == "brave":
                    installed[i] = getBrave(software.get(i)[oper])
                elif i == "chrome" or i == "edge":
                    installed[i] = getChromium(software.get(i)[oper])
                elif i == "firefox" or i == "tor":
                    installed[i] = getFirefox(software.get(i)[oper])
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                installed[i] = False
    else:
            installed = getLinuxVer(installed)
    
    print("[OK]") 
    #except:
       # onFail()


    print("Saving data...",end='\t')
    try:
        f = open("data.json",'w')
        f.write(json.dumps(installed,indent='\t'))
        f.close()
        print("[OK]")
    except:
        onFail()

    print("Testing internet connection...",end="\t")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname("captive.apple.com"), 80))
        s.send("GET / HTTP/1.1\r\nHost:captive.apple.com\r\n\r\n".encode())
        handshake = s.recv(4096).decode()
        if "Success" in handshake: 
            print("[OK]")
        else: 
            print("Connection error.") 
    except:
        onFail(True)

    comm = subprocess.Popen(["python3","communicator.py",unique,"&"])

if __name__ == '__main__':
    print("Importing libaries...",end='\t')
    main()
