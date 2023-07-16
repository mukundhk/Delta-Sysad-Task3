import os
import socket

SERVER_HOSTNAME = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOSTNAME, SERVER_PORT))

    while True:

        try:
            data_from_server = client.recv(1024).decode()
            cmd, msg = data_from_server.split(":")


            if cmd == "DISCONNECTED":
                print(f"[SERVER]: {msg}")
                break
            elif cmd == "LOGIN":
                print(f"{msg}")
                print("Enter credentials -")
                username=input("Username   :")
                password=input("Password   :")

                client.send(f"{username}:{password}".encode())
                continue
            elif cmd == "OK":
                print(f"{msg}")
            
                
            opt = input("> ").strip().lower()

            if opt == "help":
                client.send(opt.encode())

            elif opt == "logout":
                client.send(opt.encode())
                break

            elif opt == "list":
                client.send(opt.encode())

            elif opt == "delete":
                filename = input("Enter path: ")
                client.send(f"{opt}:{filename}".encode())

            elif opt == "upload":
                path = input("Enter full path: ")
                if os.path.isfile(path):
                    with open(f"{path}", "r") as f:
                        text = f.read()
                    filename = path.split("/")[-1]
                    send_data = f"{opt}:{filename}:{text}"
                    client.send(send_data.encode())
                else :
                    print("File doesnt exist")
                    send_data="FILE_DOESNT_EXIST"
                    client.send(send_data.encode())
                
            elif opt == "download" :
                filename = input("Enter filename: ")
                client.send(f"{opt}:{filename}".encode())
                data = client.recv(1024).decode()
                data = data.split(":")
                filename = data[0]
                
                if filename == "File not found." :
                    print(filename)
                else :
                    text = data[1]
                    with open(filename, "w") as f:
                        f.write(text)
                    print(f"{filename} downloaded")         
            else:
                client.send(opt.encode())
        except KeyboardInterrupt:
            break

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    start_client()