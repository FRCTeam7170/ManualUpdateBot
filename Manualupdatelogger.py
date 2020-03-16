#/usr/bin/env python3

import os
import ast
import ssl
import sys
import json
import diff
import PyPDF2
import smtplib
import datetime
import configparser
import urllib.request


config = configparser.ConfigParser()
config["internal"] = {}
config["internal"]["conf_file"] = "/etc/FRCUpdatelogger.conf"
config["internal"]["keys"]      = "['port','user','host','sender_email','password','destination','slackBot','slackBottest']"     

class Pdf_firstrobotics:
    def __init__(self):
        email           = True
        slack           = True
        test            = False
        date_now        = datetime.datetime.strftime(datetime.datetime.now(), "%m-%d-%Y")
        self.pdfPath    = os.getcwd() + "/pdf/"
        filename        = self.pdfPath + date_now + "FRCGamesManual.pdf"
        difference      = False
        
        #Notification("Update logger deactivated. Thank you for the awesome season.", False, False, False)
        
        if not os.path.isdir("pdf"):
            os.mkdir("pdf")
        if not os.path.isdir("old"):
            os.mkdir("old")
                
        if len(os.listdir(self.pdfPath)) == 0:
            self.getPDF(filename)
            sys.exit()
        else:
            self.getPDF(filename)
            difference = self.compare()
            
        if difference:
            data = self.findDifference()
            Notification(data, email, slack, test)
            
    def getPDF(self, filename):
        """Downloads PDF"""
        url      = "https://firstfrc.blob.core.windows.net/frc2020/Manual/2020FRCGameSeasonManual.pdf"
        try:
            urllib.request.urlretrieve(url, filename)
        except Exception as e:
            Notification(e, True, False, False)
        
    def compare(self):
        """Compares old PDF and new PDF based on the Document Metadata"""
        files   = os.listdir(self.pdfPath)
        f0      = self.pdfPath + files[0]
        f1      = self.pdfPath + files[1]
        if PyPDF2.PdfFileReader(f0).getDocumentInfo() == PyPDF2.PdfFileReader(f1).getDocumentInfo():
            os.remove(f1)
            return False
        else:
            return True
        
    def findDifference(self):
        """If there is a difference in the Metadata, it compares all pages and outputs the most different ones"""
        files   = sorted(os.listdir(self.pdfPath))
        f0      = self.pdfPath + files[0]
        f1      = self.pdfPath + files[1]
        print(f0, f1)
        dif, significant = diff.pdfdiff(f0, f1)
        os.rename(f0, os.getcwd() + "/old/" + files[0])
        return dif
    
class Notification:
    def __init__(self, data, email, slack, test):
        if os.path.isfile(config["internal"]["conf_file"]):
            config.read(config["internal"]["conf_file"])
            if "FRCUpdatelogger" not in config:
                print("wrong config file " + config["internal"]["conf_file"])
                sys.exit(1)
            for k in ast.literal_eval(config["internal"]["keys"]):
                if k not in config["FRCUpdatelogger"]:
                    print("key " + k + " not in " + config["internal"]["conf_file"])
                    sys.exit(1)
        else:
            print("file " + config["internal"]["conf_file"] + " not found")
            
        port            = config["FRCUpdatelogger"]["port"]
        user            = config["FRCUpdatelogger"]["user"]
        smtp_server     = config["FRCUpdatelogger"]["host"]
        sender_email    = config["FRCUpdatelogger"]["sender_email"]
        receiver_email  = config["FRCUpdatelogger"]["destination"]
        password        = config["FRCUpdatelogger"]["password"]
        if test:
            slackURL        = config["FRCUpdatelogger"]["slackBot"]
        else:
            slackURL        = config["FRCUpdatelogger"]["slackBot"]
        
        if slack:
            self.slack(data, slackURL)
        if email:
            self.mail(data, port, user, smtp_server, sender_email, receiver_email, password)
        
    def mail(self, data, port, user, smtp_server, sender_email, receiver_email, password):
        """Sends email notification"""
        message         = """Subject: Manual update logger
        
            """ + str(data)
        
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(smtp_server, port, context=context)
        server.login(user, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
            
    def slack(self, data, slackURL):
        """Sends slack notification"""
        from urllib import request
        text = "New Manual version detected: " + str(data)
        post = {"text": "{0}".format(text)}
     
        try:
            json_data = json.dumps(post)
            req = request.Request(slackURL,
                                  data=json_data.encode('ascii'),
                                  headers={'Content-Type': 'application/json'}) 
            resp = request.urlopen(req)
        except Exception as em:
            print("EXCEPTION: " + str(em))
            
if __name__ == "__main__":   
    Pdf_firstrobotics()





