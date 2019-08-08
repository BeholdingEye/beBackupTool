#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backup functions for reading configuration and saving compressed tar file
"""

import sys, os, time, tarfile


def read_backup_files_config(configBackupPrefs):
    """
    Reads file configuration from passed list of dicts, returning list 
    of lists of file paths
    """
    backupObjects = []
    for bo in configBackupPrefs:
        filesToArchive = []
        if not isinstance(bo, dict) \
                or "Backup-Folder" not in bo \
                or not bo["Backup-Folder"] \
                or not os.path.exists(bo["Backup-Folder"]):
            continue
        for dp, ds, fs in os.walk(bo["Backup-Folder"]):
            #print("dp:", dp)
            #print("ds:", ds)
            #print("fs:", fs)
            excludeFolder = False
            for ef in maybe_none(bo, "Exclude-Folders"):
                if os.path.join(dp, "") == os.path.join(ef, ""):
                    excludeFolder = True
                    break
            if not excludeFolder:
                # Append non-excluded folder, without trailing slash
                dp = dp[:-1] if dp[-1] == "/" or dp[-1] == "\\" else dp
                filesToArchive.append(dp)
                for f in fs:
                    excludeFile = False
                    for efl in maybe_none(bo, "Exclude-Files"):
                        if os.path.join(dp, f) == efl:
                            excludeFile = True
                            break
                    if not excludeFile:
                        excludeExt = False
                        for ex in maybe_none(bo, "Exclude-Extensions"):
                            ex = ex if ex.startswith(".") else "."+ex
                            if ex == os.path.splitext(f)[1]:
                                excludeExt = True
                                break
                        if not excludeExt:
                            # Append non-excluded file
                            filesToArchive.append(os.path.join(dp, f))
        #print("Files to archive in '%s':" % bo["Backup-Folder"])
        #[print("  %s" % x) for x in filesToArchive]
        backupObjects.append(filesToArchive)
    return backupObjects


def maybe_none(tDict, tItem):
    """
    Test for list item in dict and return it or empty list
    """
    if not isinstance(tDict, dict) or not tDict or tItem not in tDict \
                                    or not tDict[tItem] or not len(tDict[tItem]):
        return []
    return tDict[tItem]


def create_tar_filepath(tarDir, tarNameStem, tarUseTimestamp, tarStampFormat):
    """
    Creates tar filepath using tar file configuration
    """
    tms = get_timestamp_for_tarfile(tarUseTimestamp, tarStampFormat)
    if tms: tms = "_" + tms
    tarPath = os.path.join(tarDir, tarNameStem + tms + ".tgz")
    return tarPath


def get_timestamp_for_tarfile(tarUseTimestamp, tarStampFormat):
    """
    Returns timestamp according to passed prefs
    """
    notime = ""
    if tarUseTimestamp:
        if tarStampFormat == "seconds":
            timenow = int(time.time())
            return str(timenow)
        else: return notime
    else: return notime


def delete_old_tarfiles(tarDir, tarNameStem, tarDeleteDelay):
    """
    Deletes old tarfiles according to prefs, returns report of num of deletions or error
    """
    # Get old tar files
    if not os.path.exists(tarDir):
        return "ERROR: Directory for tar files does not exist"
    deletedCount = 0
    for dp, ds, fs in os.walk(tarDir): # TODO scandir()
        for f in fs:
            if f.startswith(tarNameStem):
                try:
                    fb, fx = os.path.splitext(f)
                    if fx != ".tgz":
                        continue
                    # Only delete if timestamp is used as part of file name, otherwise
                    # assume that tar files are overwritten on each save
                    fts = int(fb.rsplit("_", maxsplit=1)[1])
                except Exception:
                    continue
                if is_time_to_delete_tar(tarDeleteDelay, fts):
                    # Delete file
                    try:
                        os.remove(os.path.join(dp, f))
                    except Exception:
                        # If we can't delete a file, we might as well bail
                        return "ERROR: file '%s' could not be deleted" % os.path.join(dp, f)
                    deletedCount += 1
            else:
                continue
        break
    return "Number of old tar files deleted: %d" % deletedCount


def is_time_to_delete_tar(deleteDelay, fileTimestamp):
    """
    Returns bool whether *fileTimestamp* is old enough for deletion 
    specified with *deleteDelay*
    """
    ddsecs = deleteDelay * 24 * 60 * 60
    secsNow = int(time.time())
    deletableTime = secsNow - ddsecs
    if fileTimestamp <= deletableTime: return True
    else: return False


def write_tar_file(backupObjects, tarFilePath):
    """
    Writes backup files to compressed tar file
    
    Documentation is not quite clear on the closing of tar files, so we
    handle this with caution
    
    The *backupObjects* parameter is assumed to be obtained from the 
    read_backup_files_config() function and cannot cause an error
    
    Return value is a tuple of tar file path and any error message
    """
    origCWD = os.getcwd()
    returnError = ""
    # Write the file
    try:
        tar = tarfile.open(tarFilePath, "w:gz")
        for filesToArchive in backupObjects:
            # Wrestle the containing dir of the backup dir from its (non)slashed path
            bkpDirContainer = os.path.dirname(os.path.dirname(os.path.join(filesToArchive[0], "")))
            os.chdir(bkpDirContainer)
            print("Adding backup files in '%s':" % bkpDirContainer)
            for fName in filesToArchive:
                relfName = os.path.relpath(fName)
                tar.add(relfName, recursive=False)
                print("  %s" % relfName)
    except Exception as e:
        print(e)
        returnError = "ERROR: %s %s" % (sys.exc_info()[0], sys.exc_info()[1])
    finally: # Always runs
        try: tar.close()
        except Exception: pass
        os.chdir(origCWD)
    return tarFilePath, returnError


def main_test():
    """
    Run tests on objects in this module
    """
    print("Main test in backup")
    # Test the file config reader by running it on this package
    bkpDir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "")
    BACKUP_FILES = [
                        {
                            "Backup-Folder"         :   bkpDir,
                            
                            "Exclude-Folders"       :   [
                                                            os.path.join(bkpDir, "__pycache__"),
                                                            "/non/existent/folder",
                                                        ],
                                                        
                            "Exclude-Files"         :   [
                                                            os.path.join(bkpDir, "__init__.py"),
                                                            os.path.join(bkpDir, "modules/sendEmail.py"),
                                                            "/non/existent/file",
                                                        ],
                                                        
                            "Exclude-Extensions"    :   [
                                                            "pyc",
                                                            ".md",
                                                            ".txt",
                                                        ],
                        },
                        {
                            "Backup-Folder"         :   "/non/existent/folder",
                            
                            "Exclude-Folders"       :   [
                                                        ],
                                                        
                            "Exclude-Files"         :   [
                                                        ],
                                                        
                            "Exclude-Extensions"    :   [
                                                            ".py",
                                                        ],
                        },
                        {},
                    ]
    backupObjects = read_backup_files_config(BACKUP_FILES)
    assert len(backupObjects) == 1 # Second and third objects not in
    confFiles = backupObjects[0]
    assert len(confFiles) > 0
    assert "/non/existent/folder" not in confFiles
    assert "/non/existent/file" not in confFiles
    assert os.path.join(bkpDir, "__pycache__") not in confFiles
    assert os.path.join(bkpDir, "modules/sendEmail.py") not in confFiles
    assert os.path.join(bkpDir, "README.md") not in confFiles
    assert os.path.join(bkpDir, "LICENSE") not in confFiles
    assert os.path.join(bkpDir, "__init__.py") not in confFiles
    assert os.path.join(bkpDir, "BackupApp.py") in confFiles
    assert os.path.join(bkpDir, "config.py") in confFiles
    assert os.path.join(bkpDir, "modules") in confFiles
    assert os.path.join(bkpDir, "modules/backup.py") in confFiles
    if os.path.join(bkpDir, "modules/__pycache__") in confFiles:
        pycFailed = False
        for fp in confFiles:
            if os.path.splitext(fp)[1] == ".pyc":
                pycFailed = True
                break
    assert not pycFailed, "Exclusion of .pyc files failed"
    
    # Test create_tar_filepath(), including get_timestamp_for_tarfile()
    #   No timestamp
    assert create_tar_filepath("/test/dir/", "fileName", False, "seconds") == "/test/dir/fileName.tgz"
    assert create_tar_filepath("/test/dir/", "fileName", True, "days") == "/test/dir/fileName.tgz"
    #   With timestamp
    ts = int(time.time())
    tsPath = create_tar_filepath("/test/dir/", "fileName", True, "seconds")
    tsName, tsX = os.path.splitext(tsPath)
    tsBaseName, tsTS = tsName.rsplit("_", maxsplit=1)
    assert tsBaseName == "/test/dir/fileName"
    assert 0 <= int(tsTS) - ts < 2
    
    # Test is_time_to_delete_tar()
    #   Delay is 2 days, but timestamp is one second less, should return False
    fileTimestamp = int(time.time()) - (2*24*60*60 - 1)
    deleteDelay = 2
    assert not is_time_to_delete_tar(deleteDelay, fileTimestamp)
    #   Delay is 2 days, but timestamp is one second more, should return True
    fileTimestamp = int(time.time()) - (2*24*60*60 + 1)
    deleteDelay = 2
    assert is_time_to_delete_tar(deleteDelay, fileTimestamp)
    
    # Partly test delete_old_tarfiles()
    assert delete_old_tarfiles("/d09bjdjk988dnx98sjkjbxbv?dAKqiA@d", "a", 0) == "ERROR: Directory for tar files does not exist"
    assert delete_old_tarfiles("/tmp", "test", 0) == "Number of old tar files deleted: 0"
    assert delete_old_tarfiles("/tmp", "test", 10) == "Number of old tar files deleted: 0"
    
    # Test tarfile
    savedTarFile, tarError = write_tar_file(backupObjects, os.path.join("/tmp", "testtarfile.tgz"))
    assert os.path.exists(savedTarFile)
    if os.path.exists(os.path.join("/tmp", "testtarfile.tgz")): os.remove(os.path.join("/tmp", "testtarfile.tgz"))
    assert tarError == ""
    print("All backup tests passed OK")
    return 0


if __name__ == "__main__":
    main_test()
