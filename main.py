print("Importing libaries...",end='\t')
from helpers import *
import socket
import platform
import os
import subprocess
import json

print("[OK]")

def onFail(critical=False):
	print("[FAIL]")
	if critical: 
		print("Critical Error! Exiting...")
		exit(0)

def main():	
    print("Scanning OS...",end="\t")
    try:
        os = platform.system().lower()
        if os == "darwin":
            os = "macos"
        print("[OK]")
    except:
        onFail(True)

    print("Scanning software...")
    installed = {}
    f = open("paths.json",'r')
    software = f.read()
    f.close()
    software = json.loads(software)
    
    for i in software.keys():
        try:
            if i == "brave":
                installed[i] = getBrave(software.get(i)[os])
            elif i == "chrome" or i == "edge":
                installed[i] = getChromium(software.get(i)[os])
            elif i == "firefox" or i == "tor":
                installed[i] = getFirefox(software.get(i)[os])
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            installed[i] = False

    print("Getting OS version...",end='\t')
    try:
        if os == "macos":
            osVer = subprocess.run(["sw_vers","-buildVersion"], capture_output=True).stdout.decode()[:-1]
        elif os == "windows": #Windows
            osVer = platform.platform()
        else: #Linux
            osVer = subprocess.run(["uname","-r"], capture_output=True).stdout.decode()[:-1]
        installed["osVer"] = osVer
        print("[OK]")
    except:
        onFail()

    print("Phoning home...",end="\t")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("17.253.37.203", 80))
        s.send("GET / HTTP/1.1\r\nHost:captive.apple.com\r\n\r\n".encode())
        handshake = s.recv(4096).decode()
        if "Success" in handshake: 
            print("[OK]")
        else: 
            print("Connection error.") 
    except:
        onFail(True)

    print("Sending collected data...",end='\t')

    print("[OK]")
    
    print(installed)

if __name__ == '__main__':
	main()
