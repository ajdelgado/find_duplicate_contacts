#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script is licensed under GNU GPL version 2.0 or above
# (c) 2022 Antonio J. Delgado
# __description__

import sys
import os
import logging
import click
import click_config_file
from logging.handlers import SysLogHandler
import vobject

class find_duplicate_contacts:

    def __init__(self, debug_level, log_file, directory):
        ''' Initial function called when object is created '''
        self.config = dict()
        self.config['debug_level'] = debug_level
        if log_file is None:
            log_file = os.path.join(os.environ.get('HOME', os.environ.get('USERPROFILE', os.getcwd())), 'log', 'find_duplicate_contacts.log')
        self.config['log_file'] = log_file
        self._init_log()

        self.directory = directory
        self.entries = list()
        for entry in os.scandir(directory):
            self.entries.append(entry)

        self.process_entries()

    def process_entries(self):
        for entry in self.entries:
            with open(entry.path, 'r') as filep:
                content=filep.read()
            card = vobject.readOne(content)
            print(entry.path)
            print(card.contents.keys())
            sys.exit(0)
            


    def _init_log(self):
        ''' Initialize log object '''
        self._log = logging.getLogger("find_duplicate_contacts")
        self._log.setLevel(logging.DEBUG)

        sysloghandler = SysLogHandler()
        sysloghandler.setLevel(logging.DEBUG)
        self._log.addHandler(sysloghandler)

        streamhandler = logging.StreamHandler(sys.stdout)
        streamhandler.setLevel(logging.getLevelName(self.config.get("debug_level", 'INFO')))
        self._log.addHandler(streamhandler)

        if 'log_file' in self.config:
            log_file = self.config['log_file']
        else:
            home_folder = os.environ.get('HOME', os.environ.get('USERPROFILE', ''))
            log_folder = os.path.join(home_folder, "log")
            log_file = os.path.join(log_folder, "find_duplicate_contacts.log")

        if not os.path.exists(os.path.dirname(log_file)):
            os.mkdir(os.path.dirname(log_file))

        filehandler = logging.handlers.RotatingFileHandler(log_file, maxBytes=102400000)
        # create formatter
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.DEBUG)
        self._log.addHandler(filehandler)
        return True

@click.command()
@click.option("--debug-level", "-d", default="INFO",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        case_sensitive=False,
    ), help='Set the debug level for the standard output.')
@click.option('--log-file', '-l', help="File to store all debug messages.")
@click.option("--directory", "-d", help="Directory containing vCard files to check.")
@click_config_file.configuration_option()
def __main__(debug_level, log_file, directory):
    return find_duplicate_contacts(debug_level, log_file, directory)

if __name__ == "__main__":
    __main__()

