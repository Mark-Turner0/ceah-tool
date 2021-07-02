from helpers import onFail
import socket
import json


def communicate(unique):
    try:
        print("Sending data...", end='\t')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostname(), 1701))
        s.send(str("SYN " + unique).encode())
        assert s.recv(4096).decode() == "ACK " + unique

        f = open("data.json", 'r')
        data = f.read()
        f.close()
        s.send(data.encode())
        assert s.recv(4096).decode() == data
        s.send(str("ACK " + unique).encode())
        print("[OK]")

        print("Receiving response...", end='\t')
        checked = json.loads(s.recv(4096).decode())
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
