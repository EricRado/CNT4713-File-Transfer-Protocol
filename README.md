# CNT4713-File-Transfer-Protocol
Project for Net Centric Computing class 


First off two ftp client threads have been included in the submission. The ftp
client labeled TESTER is used for automating tests with a text file.

TESTING
In order to run an automated test my program requires an input of the test file
name so the test file needs to be in the same directory as ftpclientTESTER.py
program. The tester has been modified to run with flags which are set after
reading the file line by line.

FTP USERS FILE
Included in the directory of the submission is an ftpUsers.txt which contains
all of my users used for my automated tests. In addition each user has a root
directory specified in the format of "user_nameofuser" and for an admin the
format is "admin_nameofuser". Some directories and files have been created in
each of the directories for testing purposes.

RUNNING REGULAR PROGRAM
A test file is not needed to run this program. Every input is determined by
typing into the keyboard by a client. In order to run most commands you need to
login in first to a valid ftp account. A user is allowed to have 3 attempts
specified in my configuration file before that user is locked and not allowed to
login in back to the server.

SERVER
To initiate connection the server communicates with the ftp service port of
another program called ftpConnect.py which is only allowed for the admin. The
server allows a maximum of 10 connections specified in the configuration file
before the server terminates for overloading.Was not able to implement a graceful shutdown for the server. Control z has to be implemented to terminate server.
