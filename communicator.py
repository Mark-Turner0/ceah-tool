from helpers import onFail
import socket
import json
import ssl


def recvLarge(s):
    message = ""
    while True:
        buff = s.recv(4096).decode()
        if buff == "EOF":
            return message
        message += buff


def communicate(unique):
    try:
        print("Sending data...", end='\t\t')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        s.connect((socket.gethostbyname("app.markturner.uk"), 1701))
        s = context.wrap_socket(s, server_hostname="app.markturner.uk")
        s.send(str("SYN " + unique).encode())
        assert s.recv(4096).decode() == "ACK " + unique

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

        notif = s.recv(4096).decode()
        f = open("notif.txt", 'w')
        f.writelines(notif)
        f.close()
        s.send(str("ACK " + unique).encode())

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
