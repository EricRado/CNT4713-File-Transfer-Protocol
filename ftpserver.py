from socket import *
from threading import *
import os,time,configparser

hostname = 'cnt4713.cs.fiu.edu'
ftpPort = 0
dataPortMin = 0
dataPortMax = 0
class ftpClientThread(Thread):

    userName = ''
    userPass = ''
    def __init__(self,addr,sock,adminSock,path,attempts):
        Thread.__init__(self)
        self.addr = addr
        self.sock = sock
        self.passive = False

        #contains root directory
        self.cwd = os.path.join(os.getcwd(),path)

        self.mode = 'A'
        self.debugMode = False
        self.loginAttempts = 0

        #variables corresponding to user 
        self.permission = ''
        self.password = ''
        self.userName = ''
        self.personalDirectory = ''

        #contain max login attempts
        self.maxAttempts = attempts
        
        #socket only to be used by the admin
        self.adminSocket = adminSock
        print("New server socket thread started for : ")

    def runServerCmds(self,tokens):
        
        selection = tokens[0].upper()
   
        if(selection == 'USER'):
            self.userName, self.password = self.user(tokens[1])

        if(selection == 'QUIT'):
            self.quit()
            if(self.permission == 'admin'):
                self.adminSocket.send('DISABLED'.encode())
                self.adminSocket.close()
            return True

        if(selection == 'LOGOUT'):
            self.logout(self.userName)

        if(selection == 'PWD'):
            self.pwd()

        if(selection == 'DELE'):
            self.delete(tokens[1])

        if(selection == 'STOR'):
            self.stor(tokens)

        if(selection == 'RETR'):
            self.retr(tokens)

        if(selection == 'LIST'):
            self.ls(tokens)

        if(selection == 'MKDIR'):
            self.mkdir(tokens[1])

        if(selection == 'RNFR'):
            self.rnfr(tokens[1])

        if(selection == 'RMDIR'):
            self.rmdir(tokens[1])

        if(selection == 'CD'):
            self.cd(tokens[1])

        if(selection == 'CDUP'):
            self.cdup()
        
        if(selection == 'PORT'):
            self.port(tokens)

        if(selection == 'NOOP'):
            self.noop()

        if(selection == 'DEBUG'):
            self.debug(tokens[1])

        if((selection == 'TYPE') or (selection == 'ASCII') or (selection == 'IMAGE')):
            self.type(selection,tokens)

        return False

    def debug(self,tokens):
        choice = tokens.upper()
        print(choice)
        if (choice == 'ON'):
            self.debugMode = True
            self.sock.send('-->200 debug on.'.encode())
        elif(choice == 'OFF'):
            self.debugMode = False
            self.sock.send('200 debug off.'.encode())
        else:
            self.sock.send('Invalid command'.encode())
    
    def noop(self):
        self.sock.send('200 OK.'.encode())

    def type(self,selection,tokens):
        #type to be determined by user input
        if (selection == 'TYPE'):
           choice = tokens[1].upper()
           print(choice)
           if(choice == 'B'):
               self.mode = 'B'
               if(not self.debugMode):
                   self.sock.send('200 Binary mode.'.encode())
               else:
                    self.sock.send('-->200 Binary mode.'.encode())
           elif(choice == 'A'):
                self.mode = 'A'
                if(not self.debugMode):
                    self.sock.send('200 ASCII mode.'.encode())
                else:
                    self.sock.send('-->200 ASCII mode.'.encode())
           else:
                if(not self.debugMode):
                    self.sock.send('Option not valid.'.encode())
                else:
                    self.sock.send('-->Option not valid.'.encode())

        #type ascii without client input
        if (selection == 'ASCII'):
            self.mode = 'A'
            if(not self.debugMode):
                self.sock.send('200 ASCII mode.'.encode())
            else:
                self.sock.send('-->200 ASCII mode.'.encode())

        #type binary without client input
        if (selection == 'IMAGE'):
            self.mode = 'I'
            if(not self.debugMode):
                self.sock.send('200 Binary mode.'.encode())
            else:
                self.sock.send('-->200 Binary mode.'.encode())
    
    def passwordLogin(self,password):
        while(self.loginAttempts < self.maxAttempts):
            #password from client input
            passCmd = self.sock.recv(1024).decode()
    
            if(password == passCmd):
                return True
                break
            else :
                if(not self.debugMode):
                    self.sock.send('530 Login or password incorrect.'.encode())
                else:
                    self.sock.send('-->530 Login or password incorrect.'.encode())
                self.loginAttempts = self.loginAttempts + 1
    
        return False
    
    def user(self,user):
        #username from client input
        self.userName = user
        foundUser = False
        numLine = 0

        with open ('ftpUsers.txt') as file:
            data = file.readlines()
            for line in data:
                words = line.split()
                if (words[0] == self.userName):
                    if(not self.debugMode):
                        self.sock.send('331 User name okay, need password'.encode())
                    else:
                        self.sock.send('-->331 User name okay, need password'.encode())
                    foundUser = True
                    break
                numLine = numLine + 1
        
        #if user not found sends alert to client
        if not foundUser:
            if(not self.debugMode):
                self.sock.send('User not found'.encode())
            else:
                self.sock.send('-->User not found'.encode())
            return '',''

        #password from user txt file will be compared to client input password
        self.password = words[1]

        #returns true if password is valid
        passwordCheck = self.passwordLogin(self.password)
        self.permission = words[2]

        #checks if user is allowed before logging in
        if(self.permission == 'notallowed'):
            if(not self.debugMode):
                self.sock.send('530 User is not allowed to login into ftp server'.encode())
            else:
                self.sock.send('-->530 User is not allowed to login into ftp server'.encode())
            return '',''
        elif (self.permission == 'locked'):
            if(not self.debugMode):
                self.sock.send('530 User is locked from logging into ftp server'.encode())
            else:
                self.sock.send('-->530 User is locked from logging into ftp server'.encode())
            return '',''

        #user logins in to server and is directed to his directory if true
        if (passwordCheck):
            if(not self.debugMode):
                self.sock.send('230 User logged in.'.encode())
            else:
                self.sock.send('-->230 User logged in.'.encode())

            print(self.userName + " has logged on to the ftp server")

            if(self.permission == 'admin'):
                path = 'admin_' + self.userName
            else:
                path = 'user_' + self.userName

            #personalDirecotry keeps the user folder path for directory changes
            self.personalDirectory = os.path.join(self.cwd,path)
            self.cwd = os.path.join(self.cwd,path)
        else:
            userLine = self.userName + ' ' + self.password + ' ' + 'locked \n'

            infile = open('ftpUsers.txt','r+')
            content = infile.readlines()
            content[numLine] = userLine
            infile.close
            infile = open('ftpUsers.txt','w')
            infile.close
            infile = open('ftpUsers.txt','r+')
            for item in content:
                infile.write(item)
            infile.close()

            #reset user information
            self.password = ''
            self.userName = ''
            self.permission = ''

        self.loginAttempts = 0

        return self.userName, self.password
       
    def logout(self,user):
        print('User is about to be logged out : ' + user)

        if(not self.debugMode):
            self.sock.send('220 Command okay, user is logged out'.encode())
        else:
            self.sock.send('-->220 Command okay, user is logged out'.encode())

        #reset all self variables of client thread
        self.userName = ''
        self.password = ''
        self.permission = ''
        self.personalDirectory = ''

    def quit(self):
        if(not self.debugMode):
            self.sock.send('221 Service closing control connection.'.encode())
        else:
            self.sock.send('-->221 Service closing control connection.'.encode())
        self.sock.close()

    def pwd(self):
        directory = self.cwd
        self.sock.send(directory.encode())

    def mkdir(self,tokens):
        directory = os.path.join(self.cwd,tokens)

        #checks if directory exists before creating it
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            if(not self.debugMode):
                self.sock.send('212 Directory already exists'.encode())
            else:
                self.sock.send('-->212 Directory already exists'.encode())
            return None
        if(not self.debugMode):
            self.sock.send('212 Directory created.'.encode())
        else:
            self.sock.send('-->212 Directory created.'.encode())
            
    def rnfr(self,fileName):
        origFileName = os.path.join(self.cwd,fileName)
        if (os.path.isfile(origFileName)):
            if(not self.debugMode):
                self.sock.send('350 Requested file action pending further information.'.
                           encode())
            else:
                self.sock.send('-->350 Requested file action pending further information.'.
                           encode())
        else:
            if(not self.debugMode):
                self.sock.send('450 Requested file action not taken. File unavailable'.
                           encode())
            else:
                self.sock.send('-->450 Requested file action not taken. File unavailable'.
                           encode())
            return None
    
        fn = self.sock.recv(1024).decode()
        newFileName = os.path.join(self.cwd,newFileName)
        os.rename(origFileName,newFileName)
        if(not self.debugMode):
            self.sock.send('250 Requested file action okay, completed.'.encode())
        else:
            self.sock.send('-->250 Requested file action okay, completed.'.encode())
        
    def delete(self,file):
        deleFile = os.path.join(self.cwd,file)

        #checks if file exists before removing it
        if(os.path.isfile(deleFile)):
            os.remove(deleFile)
            if(not self.debugMode):
                self.sock.send('250 Requested file action okay, completed.'.encode())
            else:
                self.sock.send('-->250 Requested file action okay, completed.'.encode())
        else:
            if(not self.debugMode):
                self.sock.send('450 Requested file action not taken. File unavailable.'.
                           encode())
            else:
               self.sock.send('-->450 Requested file action not taken. File unavailable.'.
                           encode())

    def stor(self,tokens):
        fileName = os.path.join(self.cwd,tokens[1])
        print('Uploading : ' + fileName)
        if (self.mode == 'I'):
            fileOut = open(fileName,'wb')
        elif (self.mode == 'A'):
            fileOut = open(fileName,'w')
        if(not self.debugMode):
            self.sock.send('150 File status okay; about to open data connection.'.encode())
        else:
            self.sock.send('-->150 File status okay; about to open data connection.'.encode())
        self.startDataSocket()
        while True:
            data = self.data_socket.recv(1024).decode()
            if not data:
                break
            fileOut.write(data)
        fileOut.close()
        self.stopDataSocket()
        if(not self.debugMode):
            self.sock.send('226 Transfer complete.'.encode())
        else:
            self.sock.send('-->226 Transfer complete.'.encode())

    def retr(self,tokens):
        fileName = os.path.join(self.cwd,tokens[1])
        print('Downloading : ' + fileName)
        if (self.mode == 'I'):
            fileDownload = open(fileName, 'rb')
        elif (self.mode == 'A'):
            fileDownload = open(fileName, 'r')
        if(not self.debugMode):
            self.sock.send('150 File status okay; about to open data connection.'.encode())
        else:
            self.sock.send('-->150 File status okay; about to open data connection.'.encode())
        data = fileDownload.read(1024)
        self.startDataSocket()
        while data:
            self.data_socket.send(data.encode())
            data = fileDownload.read(1024)
        fileDownload.close()
        self.stopDataSocket()
        if(not self.debugMode):
            self.sock.send('226 Transfer complete.\r\n'.encode())
        else:
            self.sock.send('-->226 Transfer complete.\r\n'.encode())
        
    
    def rmdir(self,direc):
        rmDirec = os.path.join(self.cwd,direc)
        print(rmDirec)

        #check if directory exists before removing
        if(os.path.isdir(rmDirec)):
            os.rmdir(rmDirec)
            if(not self.debugMode):
                self.sock.send('212 Directory removed'.encode())
            else:
                self.sock.send('-->212 Directory removed'.encode())
        else:
            if(not self.debugMode):
                self.sock.send('550 Directory does not exist'.encode())
            else:
                self.sock.send('-->550 Directory does not exist'.encode())

    def cd(self,direc):
        changeDirec = os.path.join(self.cwd,direc)

        #checks if directory exist before changing to another directory
        if(os.path.isdir(changeDirec)):
            self.cwd = os.path.join(self.cwd,changeDirec)
            if(not self.debugMode):
                self.sock.send('200 cd executed'.encode())
            else:
                self.sock.send('-->200 cd executed'.encode())
        else:
            if(not self.debugMode):
                self.sock.send('550 Directory does not exist'.encode())
            else:
                self.sock.send('-->550 Directory does not exist'.encode())
                
    def cdup(self):
        currentPath = self.cwd
        
        #a user is not allowed to cdup if he/she is in their personal root directory
        if((self.permission == 'user') and (currentPath == self.personalDirectory)):
            if(not self.debugMode):
                self.sock.send('550 Permission denied.'.encode())
            else:
                self.sock.send('-->550 Permission denied.'.encode())
        else:
            self.cwd = os.path.dirname(self.cwd)
            if(not self.debugMode):
                self.sock.send('200 cdup executed'.encode())
            else:
                self.sock.send('-->200 cdup executed'.encode())
        print(self.cwd)
    
    def ls(self,tokens):
        if(not self.debugMode):
            self.sock.send('150 The directory listing.'.encode())
        else:
            self.sock.send('-->150 The directory listing.'.encode())
        self.startDataSocket()

        for t in os.listdir(self.cwd):
            item = os.path.join(self.cwd,t)
            self.data_socket.send((item + '\r\n').encode())
        self.stopDataSocket()
        if(not self.debugMode):
            self.sock.send('226 Directory send OK.'.encode())
        else:
            self.sock.send('-->226 Directory send OK.'.encode())

    def port(self,tokens):
        tokensSplit = tokens[1].split(',')
        self.portNumber = int(tokensSplit[4])*256 + int(tokensSplit[5])
        print(self.portNumber)
        if(not self.debugMode):
            self.sock.send('200 Got port.'.encode())
        else:
            self.sock.send('-->200 Got port.'.encode())

    #starts data stream socket
    def startDataSocket(self):
        self.data_socket = socket(AF_INET,SOCK_STREAM)
        self.data_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.data_socket.connect((hostname,self.portNumber))

    #stops data stream socket
    def stopDataSocket(self):
        self.data_socket.close()
    
    def run(self):
        self.sock.send('220 Service ready for new user.'.encode())
        check = False
        while True:
              if (check):
                  break
              cmd = self.sock.recv(1024).decode()
              tokens = cmd.split()
              check = self.runServerCmds(tokens)


def main():

    config = configparser.ConfigParser()

    #Loading up configuration file
    config.read('configuration.ini')

    #enabling ftp server
    serverAllowed = config['DEFAULT']['FtpServer']
    print('Ftp server is ',serverAllowed, 'right now')

    servicePort = int(config.get('DEFAULT','FtpServicePort'))
    serverAllowed = 'ENABLED'
    initialSocket = socket(AF_INET,SOCK_STREAM)
    initialSocket.connect((hostname,servicePort))
    initialSocket.send(serverAllowed.encode())

    print(initialSocket.recv(1024).decode())
    config.set('DEFAULT','FtpServer',serverAllowed)

    welcomeMsg = config.get('DEFAULT','WelcomeMsg')
    print(welcomeMsg)

    #Setting up ftp port and port range from configuration file
    dataPortMin = int(config.get('DEFAULT','DataPortMin'))
    dataPortMax = int(config.get('DEFAULT','DataPortMax'))
    ftpPort = int(config.get('DEFAULT','FtpPort'))

    #Creating server socket
    tcpServerSocket = socket(AF_INET,SOCK_STREAM)
    tcpServerSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    tcpServerSocket.bind((hostname,ftpPort))

    #Setting up maximum connnections my server can hold
    maxConnections = int(config.get('DEFAULT','MaximumConnections'))

    #Setting up root directory
    rootPath = config.get('DEFAULT','RootFtpDirectory')

    connections = 0
    attempts = int(config.get('DEFAULT','LoginAttempts'))
    threads = []

    while (True and (initialSocket is not None)):
        print('listening for clients')
        #Checks if the max connection my server can hold has exceeded or not
        if(connections <= maxConnections):
            tcpServerSocket.listen(maxConnections)
            connectionSocket, addr = tcpServerSocket.accept()
            newThread = ftpClientThread(addr,connectionSocket,initialSocket,rootPath,attempts)
            newThread.start()
            threads.append(newThread)
        else:
            msg = config.get('DEFAULT','MaxConnMsg')
            print(msg)
            break

        
    
    for t in threads:
        t.join

main()
