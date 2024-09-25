#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script"""

import configparser
import setuptools

config = configparser.ConfigParser()
config.read('setup.cfg')

setuptools.setup(
    scripts=['find_duplicate_contacts/find_duplicate_contacts.py'],
    author="Antonio J. Delgado",
    version='1.0.0',
    name='find_duplicate_contacts',
    author_email="TXj6QGdwejbTD1iWAj2ws9pnV@susurrando.com",
    url="https://susurrando.com",
    description="Find duplicate contacts in vCard files",
    long_description="README.md",
    long_description_content_type="text/markdown",
    license="GPLv3",
    keywords=["vCard", "contacts", "duplicates"]
)
