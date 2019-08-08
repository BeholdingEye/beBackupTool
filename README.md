beBackupTool
============

### Overview

This package enables you to archive a set of folders and email the 
compressed tar `.tgz` file. A good use case is to set up a nightly cron 
for emailing the development work done on the server during the day.

### Requirements

The emailing functionality requires a local SMTP server.

This package was created and tested with Python 3.5 on Linux Debian 9 
and Ubuntu 16.04. It might not work on Mac or Windows.

### Usage

Before the tool may be used, it must be configured in the `config.py` 
file. Three dicts of settings are available, and their usage explained 
by comments above them.

* BACKUP_FILES: Folders to back up and any exclusions within

* TAR_FILE: Tar file name, timestamp format and deletion delay

* EMAIL_PREFS: To and From addresses, Subject and message Body

Activity of the tool is logged to the `log/app.log` file, with log 
rotation enabled.

### Testing

Modules of the package may be tested individually by running them as 
scripts (without the `-m` switch) on the commandline. For example:

    cd modules
    python3 backup.py

Testing the `email.py` module will email the LICENSE file, in place of a
tar file.

The whole package may be tested by running `beBackupApp.py` with the 
`--testall` commandline option:

    python3 beBackupApp.py --test

To exclude emailing from the test, use the `--test` option instead.

### Roadmap

The ability to send the tar file to Amazon AWS S3 storage will be added 
in the future.

### Changelog

2019-08-07: v1.0.0 - Initial release