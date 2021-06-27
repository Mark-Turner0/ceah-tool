import socket
import json
import sys

from main import onFail

try:
    print("Sending data...",end='\t')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 1701))
    unique = sys.argv[1]
    data = "SYN "+unique
    s.send(data.encode())
    if s.recv(4096).decode() != "ACK "+unique:
        onFail(True)
    f = open("data.json",'r')
    data = f.read()
    f.close()
    s.send(data.encode())
    handshake = s.recv(4096).decode()
    if handshake == data: 
        print("[OK]")
except ConnectionResetError as e:
    print("[SERVER CRASH]")
    onFail(e, silent=True)
except (TimeoutError, ConnectionRefusedError) as e:
    print("[SERVER DOWN]")
    onFail(e, silent=True)
