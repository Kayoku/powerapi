"""
Module stddb
"""

import os
from smartwatts.database.base_db import BaseDB


class StdoutDB(BaseDB):
    """
    StdoutDB class

    This class is mostly use for testing some actor behaviour but
    not very useful.
    """
    def __init__(self):
        pass

    def load(self):
        """ Override """
        pass

    def get_next(self):
        """ Override """
        pass

    def save(self, json):
        """ Override """
        print('['+str(os.getpid())+']' + ' new message save.')