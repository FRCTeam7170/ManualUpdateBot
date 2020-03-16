The program is built to be run on a Linux system. On a server use crontab to run the program frequently. You have to setup a config file at /etc/FRCUpdatelogger.conf. The config file should be set up like this: 
If you are not going to send E-Mails set all the E-Mail spots to blank

port = E-Mail port (465)
user = E-Mail username
host = Your E-Mail host server (smtp)
sender_email = Sender E-Mail
password = E-Mail password
destination = Receiving Email
slackBot = The Slack channel
slackBottest = The test Slack channel. You do not have to put anything in here
