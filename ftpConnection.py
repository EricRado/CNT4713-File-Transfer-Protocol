from socket import *
import configparser

def ftp_server_start(socket):
    socket.send('Ftp server activating...'.encode())
    
def ftp_server_stop(socket):
    socket.send('Ftp server deactivating...'.encode())
    socket.close()
    return socket

def main():
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    servicePort = int(config.get('DEFAULT','FtpServicePort'))

    hostName = 'cnt4713.cs.fiu.edu'

    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind((hostName,servicePort))
    serverSocket.listen(1)
    print("Listening...")
    conn,addr = serverSocket.accept()
    print("Accepted ftp server socket.")
    while conn is not None:
        response = conn.recv(1024).decode()
        print(response)
        if(response == 'ENABLED'):
            ftp_server_start(conn)
        elif(response == 'DISABLED'):
            conn = ftp_server_stop(conn)
            print("Closing...")

#Calls main function
main()

