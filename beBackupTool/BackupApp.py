#!/usr/bin/env python3
# -*- coding: utf-8 -*-

########################################################################
#                                                                      #
#                            BE Backup Tool                            #
#                                                                      #
#           Copyright 2019 Karl Dolenc, all rights reserved            #
#                                                                      #
#               Tested with Python 3.5 on Linux Debian 9               #
#                                                                      #
########################################################################

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import sys, os
import logging, logging.handlers

if "beBackupTool" not in dir():
    # Package name "beBackupTool" not defined in __main__, so relative imports
    # do not work. We must set the path and import the package explicitly,
    # then use absolute imports from it. Relative imports then work in 
    # sub-modules. We test dir() instead of __main__ for interpreter use.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import beBackupTool

from beBackupTool import config # Works in __main__ (if path and import done above) and otherwise
#from . import config # Doesn't work in __main__
from modules import backup
from modules import sendEmail


def main_run():
    """
    Run the app
    """
    # Set up logging, to "log/app.log", with 5 count rotation on 500K file size
    appLogger = logging.getLogger()
    appLogger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "log/app.log"), maxBytes=500000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y/%m/%d %I:%M:%S %p")
    handler.setFormatter(formatter)
    appLogger.addHandler(handler)
    # Read config - backup objects
    backupObjects = backup.read_backup_files_config(config.BACKUP_FILES)
    # Read config - tar file
    tarDir = config.TAR_FILE["Directory"]
    tarNameStem = config.TAR_FILE["Name-Stem"]
    tarUseTimestamp = config.TAR_FILE["Use-Timestamp"]
    tarStampFormat = config.TAR_FILE["Stamp-Format"]
    tarDeleteDelay = config.TAR_FILE.get("Delete-Delay", 0)
    # Delete old files
    deletedTars = backup.delete_old_tarfiles(tarDir, tarNameStem, tarDeleteDelay)
    print(deletedTars)
    if deletedTars.startswith("ERROR"):
        appLogger.error(deletedTars)
        sys.exit()
    else:
        appLogger.info(deletedTars)
    # Create tar archive
    tarFilePath = backup.create_tar_filepath(tarDir, tarNameStem, tarUseTimestamp, tarStampFormat)
    tarPath, tarError = backup.write_tar_file(backupObjects, tarFilePath)
    if tarError.startswith("ERROR"):
        print(tarError)
        appLogger.error(tarError)
        sys.exit()
    else:
        print("Archive '%s' created successfully" % tarPath)
        appLogger.info("Archive '%s' created successfully" % tarPath)
    # Email backup
    refusedDict, emailError = sendEmail.create_and_send_email_message(tarPath, config.EMAIL_PREFS)
    if emailError.startswith("ERROR"):
        print(emailError) # We leave deletion of tar file for another run
        appLogger.error(emailError)
        sys.exit()
    else:
        if len(refusedDict) > 0:
            print("Refused email recipients:")
            print(refusedDict)
            appLogger.warn("Refused email recipients: " + repr(refusedDict))
        print("Email sent.")
        appLogger.info("Email sent.")
    print("Backup done.")
    appLogger.info("Backup done.")
    return 0


def main_test(mode="not-email"):
    """
    Test the package
    
    The *mode* parameter may be "not-email" or "all"
    """
    print("Main test in BackupApp")
    config.main_test()
    backup.main_test()
    if mode == "all":
        sendEmail.main_test()
    print("Main test in BackupApp passed OK")
    return 0


if __name__ == "__main__":
    if "--help" in sys.argv:
        argsHelp = """
======== BackupApp in beBackupTool ========

    Commandline arguments:

        --help      Print this help message
        --test      Test the package, excluding sending email
        --testall   Test including the email sending
"""
        print(argsHelp)
    elif "--test" in sys.argv:
        main_test(mode="not-email")
    elif "--testall" in sys.argv:
        main_test(mode="all")
    else:
        main_run()

