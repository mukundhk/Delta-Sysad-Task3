import os                                                                           
import socket                                                                       
import threading                                                                    
import zipfile                                                                      
import shutil                                                                       
import mysql.connector as mysql                                                                     


SERVER_HOST = socket.gethostbyname(socket.gethostname())                                     
SERVER_PORT = 9999

def verify_user(username, password):                                    
    db = mysql.connect(
        host="db",
        database="mydb",
        user="root",
        password="password",
        port="3306"
    )                                                                      

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM users WHERE username = %s AND password = %s",(username, password))
    
    output = cursor.fetchall() 
                                                         
    cursor.close()
    db.close()

    if len(output)==1:
        return True
    else:
        return False

def compress(file_path):                                                       
    file_w_ext = file_path.split('/')[-1]
    filename = file_w_ext.split(".")[0]
    compressed_file = filename + '.zip'                                              

    with zipfile.ZipFile(compressed_file, 'w') as f:
        f.write(file_path, file_w_ext, compress_type = zipfile.ZIP_DEFLATED)                                             
    
    new_file_path = os.path.join(os.path.dirname(file_path), compressed_file)       
    shutil.move(compressed_file, new_file_path)                                       

    return compressed_file

def find_file(file_name,USER_DIR):                                                           
    file_path = os.path.join(USER_DIR, file_name)

    if os.path.isfile(file_path):               
        return file_path
    
    else:
        return None

def decompress_file(file_path):
    
    with zipfile.ZipFile(file_path, 'r') as compressed_file:
        extracted_file = compressed_file.namelist()[0]
        compressed_file.extractall(os.path.dirname(file_path))
    
    return extracted_file

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    client_socket.send("LOGIN:Welcome to the File Server.".encode())

    creds=client_socket.recv(1024).decode()
    creds=creds.split(":")
    username , password = creds[0] , creds[1]

    if verify_user(username, password):
        client_socket.send(f"OK:Welcome {username}.Type HELP to read about the list of avaliable commands".encode())
        try:
            os.mkdir(f"/data/{username}")
            USER_DIR = f"/data/{username}"
        except FileExistsError:
            pass

        
        while True:
            data = client_socket.recv(1024).decode()
            data = data.split(":")
            opt = data[0]

            if opt == "help":
                send_data = '''OK:DOWNLOAD <filename> Downloads a file from the server.
UPLOAD <path>- Upload a file to the server.
LIST- List all the files from the server.
DELETE <filename>- Delete a file from the server.
LOGOUT- Disconnect from the server.
HELP- List all the commands.'''

                client_socket.send(send_data.encode())
            
            elif opt == "logout":
                break
            
            elif opt == "list":
                files = os.listdir(USER_DIR)
                send_data = "OK:"

                if len(files) == 0:
                    send_data += "The server directory is empty"
                else:
                    send_data += "\n".join(f for f in files)
                client_socket.send(send_data.encode())

            elif opt == "delete":
                files = os.listdir(USER_DIR)
                send_data = "OK:"
                filename = data[1]

                if len(files) == 0:
                    send_data += "The server directory is empty"
                else:
                    if filename in files:
                        os.system(f"rm {USER_DIR}/{filename}")
                        send_data += "File deleted successfully."
                    else:
                        send_data += "File not found."

                client_socket.send(send_data.encode())
            
            elif opt == "upload":
                name, text = data[1], data[2]
                filepath = os.path.join(USER_DIR, name)
                with open(filepath, "w") as f:
                    f.write(text)
                compressed_file_name=compress(filepath)
                print(f"New file {compressed_file_name} created\n")    
                os.system(f"rm {filepath}")

                send_data = "OK:File uploaded successfully."
                client_socket.send(send_data.encode())
            
            elif opt == "download" :
                name = data[1]
                file_path=find_file(name, USER_DIR)
                
                if file_path is None :
                    send_data = "File not found."
                    client_socket.send(send_data.encode())

                else:
                    decompressed_file=decompress_file(file_path)
                    with open(f"{USER_DIR}/{decompressed_file}", "r") as f:
                        data = f.read()
                    send_data = f"{decompressed_file}:{data}"
                    client_socket.send(send_data.encode())
                    os.system(f"rm {USER_DIR}/{decompressed_file}")
                    client_socket.send("OK:".encode())

            elif opt == "FILE_DOESNT_EXIST" :
                send_data="OK:"
                client_socket.send(send_data.encode())
            
            elif opt == "":
                data="OK:Invalid command. Type HELP to view all commands"
                client_socket.send(data.encode())
                


        print(f"[DISCONNECTED] {client_address} disconnected\n")
        client_socket.close()
    
    else :
        client_socket.send("OK:Invalid Username or Password. Please enter valid credentials.")
        

def start_server():
    print("[STARTING] Server is starting")
    

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER_HOST}:{SERVER_PORT}.")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    start_server()