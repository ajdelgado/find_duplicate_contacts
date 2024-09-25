#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script is licensed under GNU GPL version 2.0 or above
# (c) 2022 Antonio J. Delgado
''' Find duplicate contacts '''

import sys
import os
import logging
from logging.handlers import SysLogHandler
import shutil
from pprint import pprint
import click
import click_config_file
import vobject
import deepdiff


class FindDuplicateContacts:
    '''Main class to find duplicate contacts'''

    def __init__(self, **kwargs):
        ''' Initial function called when object is created '''
        self.config = kwargs
        if 'log_file' not in kwargs or kwargs['log_file'] is None:
            self.config['log_file'] = os.path.join(
                os.environ.get(
                    'HOME',
                    os.environ.get(
                        'USERPROFILE',
                        os.getcwd()
                    )
                ),
                'log',
                '__project_codename__.log'
            )
        self._init_log()

        self.ignore_fields = [
            "prodid",
            "uid",
            "version",
            "rev",
            "x-thunderbird-etag",
            "x-mozilla-html",
            "photo"
        ]

        self.duplicates_folder = os.path.join(
            self.config['directory'],
            self.config['duplicates_destination']
        )
        if not os.path.exists(self.duplicates_folder):
            os.mkdir(self.duplicates_folder)

        self.entries = []
        for entry in os.scandir(self.config['directory']):
            self.entries.append(entry)

        self.read_cards()

        self.compare_cards()

    def read_cards(self):
        '''Read all vCards'''
        self.cards = []
        for entry in self.entries:
            self._log.debug(
                "Reading vcard '%s'...",
                entry.path
            )
            card = {}
            card['filename'] = entry.path
            card['content'] = {}
            if not entry.is_dir():
                with open(entry.path, 'r', encoding='UTF-8') as filep:
                    content=filep.read()
                if len(content) > 0:
                    vcard = vobject.readOne(content)

                for key in vcard.contents.keys():
                    if key not in self.ignore_fields:
                        card['content'][key] = list()
                        for item in vcard.contents[key]:
                            card['content'][key].append(item.value)
                self.cards.append(card)

    def compare_cards(self):
        '''Compare all vCards'''
        checked_cards = []
        count = 0
        for card in self.cards:
            count +=1
            print(f"Contact {count} of {len(self.cards)}:\b")
            duplicated = False
            for checked_card in checked_cards:
                if self.are_same_dict(card['content'], checked_card['content']):
                    duplicated = True
                    self._log.info(
                        "Totally duplicates:\n  '%s'\n  '%s",
                        card['filename'],
                        checked_card['filename']
                    )
                    shutil.move(
                        card['filename'],
                        os.path.join(self.duplicates_folder, os.path.basename(card['filename']))
                    )
                if self.are_partially_same_dict(card['content'], checked_card['content'], key='fn'):
                    if self.manual_check_cards(card, checked_card):
                        duplicated = True
            if not duplicated:
                checked_cards.append(card)
        self._log.info(
            "Found %s unique cards",
            len(checked_cards)
        )

    def manual_check_cards(self, card1, card2):
        '''Manual check of vCards'''
        cols = os.get_terminal_size()[0]
        print("#" * cols)
        print("Card#1:")
        print(f"  filename: {card1['filename']}")
        for key, value in card1['content'].items():
            print(f"  {key}: {value}")
        print("")
        print("-" * cols)
        print("Card#2:")
        print(f"  filename: {card2['filename']}")
        for key, value in card2['content'].items():
            print(f"  {key}: {value}")
        print("")
        print("-" * cols)
        print("Differences:")
        ddiff = deepdiff.DeepDiff(card1['content'], card2['content'], ignore_order=True)
        pprint(ddiff)
        advice1 = ""
        advice2 = ""
        if len(ddiff.keys()) == 1:
            if 'dictionary_item_added' in ddiff.keys():
                advice2 = "(Suggested)"
            if 'dictionary_item_removed' in ddiff.keys():
                advice1 = "(Suggested)"
        print("-" * cols)
        print(f"1 - Keep card#1 and move card#2 {advice1}")
        print(f"2 - Keep card#2 and move card#1 {advice2}")
        print('Anything else and we keep both')
        option = input('What to do?')
        if option == "1":
            shutil.move(
                card2['filename'],
                os.path.join(self.duplicates_folder, os.path.basename(card2['filename']))
            )
            return True
        elif option == "2":
            shutil.move(
                card1['filename'],
                os.path.join(self.duplicates_folder, os.path.basename(card1['filename']))
            )
            return True
        else:
            print('Doing nothing.')
            return False

    def are_partially_same_dict(self, d1, d2, key='id'):
        '''Test if two dictionaries are similar'''
        if not isinstance(d1[key], list):
            d1[key] = [ d1[key] ]
            d2[key] = [ d2[key] ]
        if d1[key][0] == d2[key][0] or d1[key][0].lower() == d2[key][0].lower():
            return True

    def are_same_dict(self, d1, d2):
        '''Test if two dictionaries are equal'''
        ddiff = deepdiff.DeepDiff(d1, d2, ignore_order=True)
        if ddiff == dict():
            return True
        else:
            if 'dictionary_item_added' in ddiff or 'dictionary_item_removed' in ddiff:
                return False
            else:
                if 'values_changed' in ddiff:
                    real_change = False
                    for key in ddiff['values_changed'].keys():
                        if isinstance(
                            ddiff['values_changed'][key]['new_value'],
                            str
                        ):
                            if (ddiff['values_changed'][key]['new_value'].lower()
                            !=
                            ddiff['values_changed'][key]['old_value'].lower()):
                                real_change = True
                    if real_change:
                        return False
                    else:
                        # print(ddiff)
                        return False

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
@click.option("--directory", "-f", required=True, help="Directory containing vCard files to check.")
@click.option(
    '--duplicates-destination',
    '-D',
    default='duplicates',
    help='Directory to move duplicates files, relative to the directory containing the vCards.'
)
@click_config_file.configuration_option()
def __main__(**kwargs):
    return FindDuplicateContacts(**kwargs)

if __name__ == "__main__":
    __main__()
