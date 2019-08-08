#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Emailing component, using settings from config to construct the email
and send it with the local SMTP server
"""

import sys, os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib


def create_and_send_email_message(tarFilePath, configEmail, testMode=False):
    """
    Create multipart email message with tar file and send it
    
    Returns tuple of *refusedDict* that may be empty, and *returnError*
    """
    returnError = ""
    refusedDict = dict()
    try:
        msg = MIMEMultipart()
        msg["Subject"] = configEmail["Subject"]
        msg["From"] = configEmail["Address-From"]
        msg["To"] = configEmail["Address-To"]
        # File part
        if testMode:
            maintype = "text"
            subtype = "plain"
            with open(tarFilePath, "rb") as fp:
                filePart = MIMEBase(maintype, subtype)
                filePart.set_payload(fp.read())
            encoders.encode_base64(filePart)
        else:
            maintype = "application"
            subtype = "octet-stream"
            with open(tarFilePath, "rb") as fp:
                filePart = MIMEBase(maintype, subtype)
                filePart.set_payload(fp.read())
            encoders.encode_base64(filePart)
        filePart.add_header("Content-Disposition", "attachment", filename=os.path.basename(tarFilePath))
        msg.attach(filePart)
        # Message text body part
        if testMode:
            textPart = MIMEText("Test message sent from sendEmail.py main_test()")
        else:
            textPart = MIMEText(configEmail["Body"])
        msg.attach(textPart)
        # Send
        msgString = msg.as_string(unixfrom=True) # Required?
        #msgString = msg.as_string()
        with smtplib.SMTP("localhost") as s:
            refusedDict = s.sendmail(configEmail["Address-From"], configEmail["Address-To"], msgString)
    except Exception as e:
        returnError = "ERROR: %s %s" % (sys.exc_info()[0], sys.exc_info()[1])
    return refusedDict, returnError


def main_test():
    """
    Test emailing by sending the package LICENSE file, using config email preferences
    """
    print("Main test in sendEmail")
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config
    thisFile = os.path.abspath(__file__)
    fp = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(thisFile))), "LICENSE")
    assert os.path.exists(fp)
    refusedDict, returnError = create_and_send_email_message(fp, config.EMAIL_PREFS, testMode=True)
    assert len(refusedDict) == 0
    if returnError != "":
        print(returnError)
    assert returnError == ""
    print("All sendEmail tests passed OK")
    return 0

if __name__ == "__main__":
    main_test()
