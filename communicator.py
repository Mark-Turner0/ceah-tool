from helpers import onFail
import socket
import json
import ssl


def checkFirewall():
    server = socket.socket()
    server.bind(("0.0.0.0", 1701))
    server.settimeout(20)
    try:
        server.listen(1)
        conn, addr = server.accept()
        if addr[0] == socket.gethostbyname("app.markturner.uk"):
            return False
    except socket.timeout:
        return True


def recvLarge(s):
    message = ""
    while True:
        buff = s.recv(4096).decode()
        if buff == "EOF":
            return message
        message += buff


def communicate(unique):
    try:
        print("Connecting to server...", end='\t')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        s.connect((socket.gethostbyname("app.markturner.uk"), 1701))
        s = context.wrap_socket(s, server_hostname="app.markturner.uk")
        s.send(str("SYN " + unique).encode())
        assert s.recv(4096).decode() == "ACK " + unique
        print("[OK]")

        print("Checking firewalls...", end='\t')
        try:
            checkFirewall()
            print("[OK]")
        except Exception as e:
            onFail(e)

        print("Sending data...", end='\t\t')
        f = open("data.json", 'r')
        data = f.read()
        f.close()
        s.send(data.encode())
        s.send("EOF".encode())
        assert recvLarge(s) == data
        s.send(str("ACK " + unique).encode())
        print("[OK]")

        print("Receiving response...", end='\t')
        checked = recvLarge(s)
        checked = json.loads(checked)
        s.send(str("ACK " + unique).encode())
        f = open("checked.json", 'w')
        f.write(json.dumps(checked, indent='\t'))
        f.close()

        notif = recvLarge(s)
        notif = json.loads(notif)
        s.send(str("ACK " + unique).encode())
        f = open("notif.json", 'w')
        f.write(json.dumps(notif, indent='\t'))
        f.close()

        assert s.recv(4096).decode() == "FIN " + unique
        s.send(str("FIN ACK " + unique).encode())
        print("[OK]")

    except ConnectionResetError as e:
        print("[SERVER CRASH]")
        onFail(e, silent=True)
    except (TimeoutError, ConnectionRefusedError) as e:
        print("[SERVER DOWN]")
        onFail(e, silent=True)
    except AssertionError as e:
        print("[DATA LOSS]")
        onFail(e, silent=True)
