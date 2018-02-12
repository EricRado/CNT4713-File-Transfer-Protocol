#import necessary packages.
import os
import os.path
import errno
import traceback
import sys
import configparser
from argparse import ArgumentParser
from socket import *

#Global constants
#USED FOR AUTOMATING TESTING PURPOSES


RECV_BUFFER = 1024
FTP_PORT = 0
CMD_QUIT = "QUIT"
CMD_HELP = "HELP"
CMD_USER = "USER"
CMD_PASS = "PASS"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_LIST = "LIST"
CMD_PWD = "PWD"
CMD_PORT = "PORT"
CMD_DELETE = "DELE"
CMD_DEL = "DEL"
CMD_STOR = "STOR"
CMD_BYE = "BYE"
CMD_RMDIR = "RMDIR"
CMD_MKDIR = "MKDIR"
CMD_CD = "CD"
CMD_RNFR = "RNFR"
CMD_PASV = "PASV"
CMD_CDUP = "CDUP"
CMD_RETR = "RETR"
CMD_NOOP = "NOOP"
CMD_TYPE = "TYPE"
CMD_ASCII = "ASCII"
CMD_IMAGE = "IMAGE"
CMD_PUT = "PUT"
CMD_GET = "GET"
CMD_DEBUG = "DEBUG"

#The data port starts at high number (to avoid privileges port 1-1024)
#the ports ranges from MIN to MAX
DATA_PORT_MAX = 0
DATA_PORT_MIN = 0
#data back log for listening.
DATA_PORT_BACKLOG = 1

#global variables
#store the next_data_port use in a formula to obtain
#a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1


#global

username = ""
password = ""
hostname = "cnt4713.cs.fiu.edu"
logged_on = False
debug_mode = False
verbose_mode = True

#Flags for testing purposes
hostFlag = 0
userFlag = 0
passwordFlag = 0
activeFlag = 0
debugFlag = 0
verboseFlag = 0
dprFlag = 0
configFlag = 0
testFileFlag = 0
defaultTFlag = 0
lFlag = 0
lallFlag = 0
versionFlag = 0
infoFlag = 0
ftpFlag = 0

#sets flags from 1st line from input test file
def setFlags(line):
    global hostFlag
    global userFlag
    global passwordFlag
    global activeFlag
    global debugFlag
    global verboseFlag
    global dprFlag
    global configFlag
    global testFileFlag
    global defaultTFlag
    global lFlag
    global lallFlag
    global versionFlag
    global infoFlag
    global ftpFlag
    global username
    global password
    global hostname

    cmdSplit = line.split()
    counter = 0
    for item in cmdSplit:

        if(item == "-h"):
            hostFlag = 1
            hostname = cmdSplit[counter +1]

        elif(item == "-u"):
            userFlag = 1
            username = cmdSplit[counter +1]

        elif(item == "-p"):
            passwordFlag = 1
            password = cmdSplit[counter + 1]

        elif(item == "-A"):
            activeFlag = 1

        elif(item == "-d" or item == "-D"):
            debugFlag = 1

        elif (item == "-V"):
            verboseFlag = 1

        elif (item == "-dpr"):
            dprFlag = 1
            dataPortRange = cmdSplit[counter + 1]

        elif(item == "-c"):
            configFlag = 1
            configFile = cdmSplit[counter + 1]

        elif (item == "-t"):
            testFileFlag = 1
            testName = cdmSplit[counter + 1]

        elif (item == "-T"):
            defaultTflag = 1
            defaultName = cdmSplit[counter + 1]

        elif(item == "-L"):
            lflag = 1
            logFileName = cdmSplit[counter + 1]

        elif(item == "-ALL"):
            lallFlag = 1
            alllogFileName = cdmSplit[counter + 1]

        elif(item == "-version"):
            versionFlag = 1

        elif(item == "-info"):
            infoFlag = 1
        elif(item == "ftp"):
            ftpFlag = 1

        counter += 1

#entry point main()
def main():
    global username
    global password
    global hostname
    global logged_on
    global FTP_PORT
    global DATA_PORT_MIN
    global DATA_PORT_MAX
    global hostFlag
    global userFlag
    global passwordFlag
    global activeFlag
    global debugFlag
    global verboseFlag
    global dprFlag
    global configFlag
    global testFileFlag
    global defaultTFlag
    global lFlag
    global lallFlag
    global versionFlag
    global infoFlag
    global ftpFlag

    #loading up configuration file
    config = configparser.ConfigParser()
    config.read('configuration.ini')

    #loading up port numbers
    FTP_PORT = int(config.get('DEFAULT', 'FtpPort'))
    DATA_PORT_MIN = int(config.get('DEFAULT', 'DataPortMin'))
    DATA_PORT_MAX = int(config.get('DEFAULT', 'DataPortMax'))

    print("FTP Client v1.0")
    print("********************************************************************")
    print("**                        ACTIVE MODE ONLY                        **")
    print("**                  USED FOR AUTOMATING TESTING PURPOSES          **")
    print("********************************************************************")
    print(("You will be connected to host:" + hostname))
    print("Type HELP for more information")
    print("Commands are NOT case sensitive\n")

    ftp_socket = ftp_connecthost(hostname)
    ftp_recv = ftp_socket.recv(RECV_BUFFER)
    ftp_code = ftp_recv[:3]

    #note that in the program there are many .strip('\n')
    #this is to avoid an extra line from the message
    #received from the ftp server.
    #an alternative is to use sys.stdout.write
    print(msg_str_decode(ftp_recv,True))


    keep_running = True

    #testFile = input("Type name of test file : ")

    #will contain commands from test file in a array
    '''
    cmdArr = []

    with open(testFile, "r") as file:
        data = file.readlines()
        for line in data:
            line.strip()
            if "#" not in line:
                cmdArr.append(line)
            else:
                continue

        #sends first line of test file to parse arguments
    setFlags(cmdArr[0])
    counter = 0
    #if a test file is being used for automate testing run the
    #following code below
    if(ftpFlag):
        for items in cmdArr:
            if(not counter):
                userMsg = "USER " + username + " " + password
                tokens = userMsg.split()
                cmdmsg,logged_on, ftp_socket = run_cmds(tokens,logged_on,ftp_socket)
            else:
                tokens = items.split()
                cmdmsg,logged_on, ftp_socket = run_cmds(tokens, logged_on,ftp_socket)
            counter = 1
    '''

    #if a user is controlling  ftp run the following code below
    if(not ftpFlag):
        while keep_running:
            try:
                rinput = input("FTP>")
                if (rinput is None or rinput.strip() == ''):
                    continue
                tokens = rinput.split()
                cmdmsg , logged_on, ftp_socket = run_cmds(tokens,logged_on,ftp_socket)
                if (cmdmsg != ""):
                    print(cmdmsg)
            except OSError as e:
            # A socket error
              print("Socket error:",e)
              strError = str(e)
              #this exits but it is better to recover
              if (strError.find("[Errno 32]") >= 0):
                  sys.exit()

    #print ftp_recv
    try:
        ftp_socket.close()
        print("Thank you for using FTP 1.0")
    except OSError as e:
        print("Socket error:",e)
    sys.exit()

def run_cmds(tokens,lin,ftp_socket):
    global username
    global password
    global hostname
    global logged_on
    global ftpFlag

    cmd = tokens[0].upper()
    cmd.strip()

    checkBye = False

    if(cmd == CMD_DEBUG):
        debug_ftp(tokens,ftp_socket)
        return "", logged_on, ftp_socket

    if ((cmd == CMD_QUIT) or (cmd == CMD_BYE)):
        if(cmd == CMD_BYE):
            checkBye = True
        quit_ftp(username,checkBye,logged_on,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_HELP):
        help_ftp()
        return "",logged_on, ftp_socket

    if((cmd == CMD_IMAGE) or (cmd == CMD_ASCII)):
        ftp_socket = mode_ftp(cmd,ftp_socket)
        return "", logged_on, ftp_socket

    if(cmd == CMD_TYPE):
        ftp_socket = type_ftp(tokens,ftp_socket)
        return "", logged_on, ftp_socket

    if(cmd == CMD_NOOP):
        ftp_socket = noop_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if (cmd == CMD_PWD):
        if logged_on:
            ftp_socket = pwd_ftp(ftp_socket)
        else:
            print("Log in first to use this feature.")
        return "",logged_on, ftp_socket

    if(cmd == CMD_CDUP):
        if logged_on:
            ftp_socket = cdup_ftp(ftp_socket)
        else:
            print("Log in first to use this feature.")
        return "", logged_on, ftp_socket

    if (cmd == CMD_MKDIR):
        if logged_on:
            ftp_socket = mkdir_ftp(tokens,ftp_socket)
        else:
            print("Log in first to use this feature.")
        return "",logged_on,ftp_socket

    if(cmd == CMD_RMDIR):
        if logged_on:
            ftp_socket = rmdir_ftp(tokens,ftp_socket)
        else:
            print("Log in first to use this feature.")
        return "", logged_on, ftp_socket

    if(cmd == CMD_CD):
        if logged_on:
            ftp_socket = cd_ftp(tokens,ftp_socket)
        else:
            print("Log in first to use this feature.")
        return "",logged_on,ftp_socket

    if (cmd == CMD_USER):
        if not logged_on:
            username, password,logged_on, ftp_socket \
            = userLogin(username,password,logged_on, tokens, ftp_socket)
        else:
            print("User is already logged in.")
        return "",logged_on, ftp_socket

    if (cmd == CMD_LOGOUT):
        if logged_on:
            username ,logged_on,ftp_socket = logout(username,logged_on,ftp_socket)
        else:
            print("No user is logged in.")

        return "",logged_on, ftp_socket

    if (cmd == CMD_DELETE or cmd == CMD_DEL):
        if logged_on:
            ftp_socket = delete_ftp(tokens,ftp_socket)
        else:
            print("Login first to use this feature.")
        return "",logged_on, ftp_socket

    if(cmd == CMD_RNFR):
        if logged_on:
            ftp_socket = rnfr_ftp(tokens,ftp_socket)
        else:
            print("Login first to use this feature.")
        return "",logged_on, ftp_socket


    if (cmd == CMD_LS or cmd == CMD_LIST):
        #FTP must create a channel to received data before
        #executing ls.
        #also makes sure that data_socket is valid
        #in other words, not None
        if(not logged_on):
            print("Login first to use this feature.")
            return "", logged_on, ftp_socket
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None ):
            ls_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[LS] Failed to get data port. Try again.",logged_on, ftp_socket


    if (cmd == CMD_STOR or cmd == CMD_PUT):
        # FTP must create a channel to received data before
        # executing put.
        #  also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            stor_ftp(tokens,ftp_socket,data_socket),logged_on, ftp_socket
            return "",logged_on, ftp_socket
        else:
            return "[STOR] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_RETR or cmd == CMD_GET):
        # FTP must create a channel to received data before
        # executing get.
        # also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            retr_ftp(tokens, ftp_socket, data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[RETR] Failed to get data port. Try again.",logged_on, ftp_socket


    return "Unknown command", logged_on, ftp_socket


def str_msg_encode(strValue):
    msg = strValue.encode()
    return msg

def msg_str_decode(msg,pStrip=False):
    #print("msg_str_decode:" + str(msg))
    strValue = msg.decode()
    if (pStrip):
        strValue.strip('\n')
    return strValue

def debug_ftp(tokens,ftp_socket):
    print(len(tokens))
    if(len(tokens) == 2):
        choice = tokens[1]
    elif(len(tokens) > 2):
        print("Specified too many inputs.")
        return None
    else:
        print("Choose on to turn on debug or off to turn off debug.")
        return None

    ftp_socket.send(str_msg_encode("DEBUG " +choice))
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    print(msg)


def ftp_connecthost(hostname):
    print('from connecthost : ', FTP_PORT)
    ftp_socket = socket(AF_INET, SOCK_STREAM)
    #to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))
    print (ftp_socket)
    return ftp_socket

def ftp_new_dataport(ftp_socket):
    global next_data_port
    dport = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1 #for next next
    dport = (DATA_PORT_MIN + dport) % DATA_PORT_MAX

    print(("Preparing Data Port: " + host + " " + host_address + " " + str(dport)))
    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, dport))
    data_socket.listen(DATA_PORT_BACKLOG)

    #send a port command

    #the port requires the following
    #PORT IP PORT
    #however, it must be transmitted like this.
    #PORT 192,168,1,2,17,24
    #where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_dport = str(dport // 256) #get high part
    low_dport = str(dport % 256) #similar to dport << 8 (left shift)
    port_argument_list = host_address_split + [high_dport,low_dport]
    port_arguments = ','.join(port_argument_list)
    cmd_port_send = CMD_PORT + ' ' + port_arguments + '\r\n'
    print(cmd_port_send)

    try:
        ftp_socket.send(str_msg_encode(cmd_port_send))
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return data_socket

def type_ftp (tokens,ftp_socket):
    if(len(tokens) < 2):
        print("Type [mode]. Please specify new mode")
    elif (len(tokens) == 2):
        ftp_socket.send(str_msg_encode("TYPE " + tokens[1]))
        msg = ftp_socket.recv(RECV_BUFFER)
        print(msg_str_decode(msg,True))
    else :
        print("Too many inputs specified")

    return ftp_socket

def mode_ftp(cmd,ftp_socket):
    ftp_socket.send(str_msg_encode(cmd))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def noop_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("NOOP\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def pwd_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("PWD\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def mkdir_ftp(tokens, ftp_socket):
    if(len(tokens) < 2):
        print("mkdir [directoryName]. Please specify new directory name")
        return ftp_socket
    elif(len(tokens) == 2):
        remote_directoryName = tokens[1]
        ftp_socket.send(str_msg_encode("MKDIR " + remote_directoryName+ "\r\n"))
    else:
        print("Too many directories were specified")
        return ftp_socket

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def retr_ftp(tokens, ftp_socket, data_socket):
    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    remote_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = remote_filename

    ftp_socket.send(str_msg_encode("RETR " + remote_filename + "\r\n"))

    print(("Attempting to write file. Remote: " + remote_filename + " - Local:" + filename))

    msg = ftp_socket.recv(RECV_BUFFER)
    strValue = msg_str_decode(msg)
    tokens = strValue.split()
    if (tokens[0] != "150"):
        print("Unable to retrieve file. Check that file exists (ls) or that you have permissions")
        return

    print(msg_str_decode(msg,True))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename, "wb")  # read and binary modes

    size_recv = 0
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = data_connection.recv(RECV_BUFFER)

        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            file_bin.write(data)
            size_recv += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


def stor_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = local_filename

    cwd = os.getcwd()
    filePath = os.path.join(cwd,local_filename)

    if (os.path.isfile(filePath) == False):
        print(("Filename does not exist on this client. Filename: " + filename + " -- Check file name and path"))
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

    ftp_socket.send(str_msg_encode("STOR " + filename + "\r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename,"rb") #read and binary modes

    size_sent = 0
    #use write so it doesn't produce a new line (like print)
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = file_bin.read(RECV_BUFFER)
        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            data_connection.send(data)
            size_sent += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))



def ls_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) > 1):
        ftp_socket.send(str_msg_encode("LIST " + tokens[1] + "\r\n"))
    else:
        ftp_socket.send(str_msg_encode("LIST\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    data_connection, data_host = data_socket.accept()

    msg = data_connection.recv(RECV_BUFFER)
    while (len(msg) > 0):
        print(msg_str_decode(msg,True))
        msg = data_connection.recv(RECV_BUFFER)

    data_connection.close()
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def delete_ftp(tokens, ftp_socket):
    if (len(tokens) < 2):
        print("dele [fileName]. Please specify a file name to delete")
        return ftp_socket
    elif (len(tokens) == 2):
        deleFile = tokens[1]
        print(("Attempting to delete... " + deleFile))
        ftp_socket.send(str_msg_encode("DELE " + deleFile + "\r\n"))
    else:
        print("Too many files were specified")
        return ftp_socket
    #runs if dele cmd succesfully sent to server
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def rnfr_ftp (tokens, ftp_socket):
    msg = ""
    if (len(tokens) < 2):
        print("You must specify a file to rename")
        return ftp_socket
    elif (len(tokens) == 2):
        fromFile = tokens[1]
        print(("Attempting to rename " + fromFile))
        ftp_socket.send(str_msg_encode("RNFR " + fromFile + "\r\n"))
    else:
        print ("Too many files were specified")
        return ftp_socket

    msg = ftp_socket.recv(RECV_BUFFER)
    msg = msg_str_decode(msg,True)
    print(msg)
    check = msg.split()
    print(check[0])
    if(check[0] == "450"):
        return ftp_socket

    newFileName = input("Specify file's new name : ")
    if (newFileName != ""):
        ftp_socket.send(str_msg_encode(newFileName))
    else:
        print("No file name was specfied.")
        return ftp_socket

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def rmdir_ftp(tokens,ftp_socket):
    if(len(tokens) < 2):
        print("rmdir [directoryName].Please specify directory name to remove")
        return ftp_socket
    elif (len(tokens) == 2):
        print("Attempting to remove " + tokens[1])
        ftp_socket.send(str_msg_encode("RMDIR " + tokens[1] + "\r\n"))
    else :
        print("Too many directories were specified")
        return ftp_socket

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def cd_ftp(tokens,ftp_socket):
    direc = tokens[1]
    if(len(tokens) < 2 ):
        print("cd [directoryName]. You must specify a directory path to change to")
        return ftp_socket
    elif(len(tokens) == 2):
        print("Attempting to cd to " + direc)
        ftp_socket.send(str_msg_encode("CD " + direc + "\r\n"))
    else:
        print("Too many directories were specified")
        return ftp_socket

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def cdup_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("CDUP \r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return ftp_socket

def logout(userName,logged_on, ftp_socket):

    #no connection in socket
    if (ftp_socket is None):
        print("Your connection was already terminated.")
        return False, ftp_socket

    #no user is logged in end function
    if (logged_on == False):
        print("You are not logged in.")
        return False, ftp_socket
    else:
        print("Attempting to log out...")
    msg = ""

    #logout cmd send to server
    try:
        ftp_socket.send(str_msg_encode("LOGOUT \r\n"))
        msg = ftp_socket.recv(RECV_BUFFER)
    except socket.error:
        print ("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False

    userName = ""
    #return logout confirmation message
    print(msg_str_decode(msg,True))
    #logged_on should now be false
    return userName,False, ftp_socket

def quit_ftp(username,byeCheck,lin,ftp_socket):
    print ("Quitting...")
    #if user is logged in they will be logged out before terminating

    if (lin):
        username,logged_on, ftp_socket = logout(username,lin,ftp_socket)

    #runs after user is logged out or not
    ftp_socket.send(str_msg_encode("QUIT \r\n"))
    msg = ftp_socket.recv(RECV_BUFFER)

    print(msg_str_decode(msg,True))
    print("Thank you for using FTP")

    #if a bye command do this
    if (byeCheck):
        print("BYE...")
    try:
        if (ftp_socket is not None):
            ftp_socket.close()
    except socket.error:
        print ("Socket was not able to be close. It may have been closed already")
    sys.exit()

#userlogin has been modified to run test files because when verifying a
#password it calls input function which will stay running if running a
#test. So ftpFlag is used to avoid this and also break out of while loop
#which allows user 3 attempts before locking the user.

def userLogin(userName,password,logged_on,tokens, ftp_socket):
    #FOR TESTING PURPOSES
    global userFlag
    global passwordFlag
    global ftpFlag

    count = 0
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    attemptLogins = int(config.get('DEFAULT','LoginAttempts'))

    #checks if their is a username input after user cmd
    if((len(tokens) == 2 ) and (tokens[1] is not None)):
        userName = tokens[1]
    #check if their is more than one input for user cmd
    elif (len(tokens) > 2 and (not ftpFlag)):
        print("Specified too many inputs")

    #check if user is followed by a blank username
    if (userName == None or userName.strip() == ""):
        print("Username is blank. Try again")
        logged_on = False
        return userName,password, logged_on, ftp_socket

    print(("Attempting to login user : " + userName))

    #send username to server to check authentication
    ftp_socket.send(str_msg_encode("USER " + userName + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)

    #prints username server confirmation message
    decodeMsg = msg_str_decode(msg,True)
    print(decodeMsg)

    if(decodeMsg == "User not found"):
        userName = ""
        logged_on = False
        return userName,password,logged_on,ftp_socket

    while(count < attemptLogins):
        if(not ftpFlag):
            password = input("Enter password : ")

        if(password == None or password.strip() == ""):
            print("Password is blank. Try again")
            logged_on = False
            return userName,password, logged_on, ftp_socket

        print("Attempting to verify password... ")

        #sends password to server to check authentication
        ftp_socket.send(str_msg_encode(password ))
        msg = ftp_socket.recv(RECV_BUFFER)
        #prints password server confirmation message
        recvMsg = msg_str_decode(msg,True)
        print (recvMsg)
        tokens = recvMsg.split()
        if (len(tokens) > 0 and tokens[0] == "530"):
            logged_on = False
            password = ""
        elif(tokens[0] == "230"):
            logged_on = True
            break
        else:
            logged_on = False
            break
        #FOR AUTOMATING PURPOSES
        if(ftpFlag):
            break
        count = count + 1

    if(tokens[0] == "230"):
        logged_on = True
    return userName,password,logged_on,ftp_socket

#REFINE TO MY NEW PROTO CODE
def help_ftp():
    print("FTP Help")
    print("Commands are not case sensitive")
    print("")
    print((CMD_QUIT + "\t\t Exits ftp and attempts to logout"))
    print(CMD_BYE + "\t\t Exits ftp and attempts to logout, send bye for confirmation.")
    print((CMD_USER + "\t\t User login. It expects username followed by a password. USER [username] [password]"))
    print((CMD_LOGOUT + "\t\t Logout from ftp but not client"))
    print((CMD_LS + "\t\t prints out remote directory content"))
    print((CMD_PWD + "\t\t prints current (remote) working directory"))
    print((CMD_RETR + " or " + CDM_GET + "\t\t gets remote file. RETR remote_file [name_in_local_system]"))
    print((CMD_STOR + " or " + CMD_PUT + "\t\t sends local file. STOR local_file [name_in_remote_system]"))
    print((CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]"))
    print(CMD_MKDIR + "\t\t creates a remote directory. MKDIR [remote_directory]")
    print(CMD_RMDIR + "\t\t removes a remote directory. RMDIR [remote_directory]")
    print(CMD_CD + "\t\t changes to specifed directory. CD [remote_directory]")
    print(CMD_CDUP + "\t\t changes to root directory of current working directory. CDUP [remote_directory]")
    print(CMD_RNFR + "\t\t renames a specifed file. RNFR [remote_file]")
    print(CMD_ASCII + "\t\t changes to ascii mode.")
    print(CMD_IMAGE + "\t\t changes to binary mode.")
    print(CMD_TYPE + "\t\t expects either a for ascii or b for image mode. TYPE [mode_type]")
    print(CMD_NOOP + " \t\t send okay message.")
    print((CMD_HELP + "\t\t prints help FTP Client"))

#Calls main function.
main()
