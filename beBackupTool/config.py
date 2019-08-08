#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration settings for various package components
"""

import sys, os

#  
#  Backup objects are specified as dicts in the BACKUP_FILES list, with
#  "Backup-Folder" specifying the folder to backup, and the rest of the 
#  object settings controlling exclusions in that folder.
#  
#  Backup and Exclude Folders and Files must be full, absolute paths.
#  
#  All values except Backup Folder may be left empty in each backup 
#  object dict, but the empty lists (and their keys) must be present.
#  
#  Folders may or may not have a trailing slash. Extensions may or may 
#  not start with a dot.
#  
#  Any required exclusions must be set for each backup object, even if 
#  they repeat. For example, if files with the ".pyc" extension should 
#  always be excluded, this must be set for every backup object.
#

BACKUP_FILES = [
    {
        "Backup-Folder"         :   "/path/to/folder/to/backup/",
        
        "Exclude-Folders"       :   [
                                    ],
                                    
        "Exclude-Files"         :   [
                                    ],
                                    
        "Exclude-Extensions"    :   [
                                    ],
    },
]

#  
#  Preferences for tar file.
#  
#  Name Stem must not be empty. 1 to 40 [A-Za-z0-9_] chars are valid.
#  
#  If Timestamp is used, a timestamp will be appended to the name,
#  before the ".tgz" file extension, separated by an underscore.
#  
#  The only timestamp format currently available is "seconds", as 
#  provided by the time.time() function (and truncated to int).
#  
#  Directory for writing the file must be accessible to the script.
#  
#  Delete Delay sets the number of days to pass before archives will be
#  deleted. If "/tmp" directory is used, deletion may happen sooner.
#  If set to 0, all existing archives will be deleted on every run of
#  this script, possibly losing data. Set the value to 1 or greater.
#  

TAR_FILE = {
                "Name-Stem"     :   "BE_Backup",
                "Use-Timestamp" :   True,
                "Stamp-Format"  :   "seconds",
                "Directory"     :   "/tmp",
                "Delete-Delay"  :   7,
            }

# 
#  Preferences for email.
# 
#  None of the fields may be empty. Subject may be up to 100 chars. Body 
#  may be up to 500 chars and must be ASCII text only.
# 

EMAIL_PREFS = {
                "Address-From"  :   "from@address.com",
                "Address-To"    :   "to@address.com",
                "Subject"       :   "Backup File",
                "Body"          :   """Latest backup file from the server""",
            }


def main_test():
    """
    Test for sane and valid config values
    """
    print("Main test in config")
    import re
    
    # Backup objects
    for bo in BACKUP_FILES:
        assert isinstance(bo["Backup-Folder"], str) and len(bo["Backup-Folder"]) > 0 and os.path.exists(bo["Backup-Folder"])
        assert isinstance(bo["Exclude-Folders"], list)
        assert not len([x for x in bo["Exclude-Folders"] if not isinstance(x, str)])
        assert isinstance(bo["Exclude-Files"], list)
        assert not len([x for x in bo["Exclude-Files"] if not isinstance(x, str)])
        assert isinstance(bo["Exclude-Extensions"], list)
        assert not len([x for x in bo["Exclude-Extensions"] if not isinstance(x, str)])
        assert not len([x for x in bo["Exclude-Extensions"] if not re.match(r"^\.?[A-Za-z]{2,10}$", x)]), "One or more Exclude-Extensions are incorrect."
    
    # Tar name
    assert len(TAR_FILE["Name-Stem"]) > 0
    assert re.match(r"[A-Za-z0-9_]{1,40}", TAR_FILE["Name-Stem"]), "Invalid Name-Stem."
    assert isinstance(TAR_FILE["Use-Timestamp"], bool)
    assert TAR_FILE["Stamp-Format"] == "seconds"
    assert os.path.exists(TAR_FILE["Directory"])
    assert isinstance(TAR_FILE["Delete-Delay"], int) and TAR_FILE["Delete-Delay"] > 0
    
    # Email
    assert len(EMAIL_PREFS["Address-From"]) > 0
    assert re.match(r"^[A-Za-z0-9_\-\.]+@[A-Za-z0-9_-]+?\.[A-Za-z]{2,10}$", EMAIL_PREFS["Address-From"]), "Invalid email address."
    assert len(EMAIL_PREFS["Address-To"]) > 0
    assert re.match(r"^[A-Za-z0-9_\-\.]+@[A-Za-z0-9_-]+?\.[A-Za-z]{2,10}$", EMAIL_PREFS["Address-To"]), "Invalid email address."
    assert 0 < len(EMAIL_PREFS["Subject"]) <= 100
    assert 0 < len(EMAIL_PREFS["Body"]) <= 500
    print("All config tests passed OK")
    return 0


if __name__ == "__main__":
    main_test()

