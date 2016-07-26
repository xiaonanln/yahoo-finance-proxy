# coding: utf8

import os
import logging
import ConfigParser

SYMBOLS_STAT_FILE = 'symbols.stat'
_SYMBOLS_SECTION = 'symbols'

configParser = ConfigParser.ConfigParser()
if os.path.exists(SYMBOLS_STAT_FILE):
    logging.info("Read symbolsdb: %s", SYMBOLS_STAT_FILE)
    configParser.read(SYMBOLS_STAT_FILE)
else:
    logging.warn("Symbolsdb file not exists")

if not configParser.has_section(_SYMBOLS_SECTION):
    configParser.add_section(_SYMBOLS_SECTION)

def get(symbol, startDate, stopDate):
    try:
        dateRange = configParser.get(_SYMBOLS_SECTION, symbol)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return None

    savedStartDate, savedStopDate = dateRange.split('~')
    if savedStartDate != startDate or savedStopDate != stopDate:
        return None

    with open('%s.db' % symbol, 'rb') as fd:
        return fd.read()

def set(symbol, startDate, stopDate, data):
    dateRange = '%s~%s' % (startDate, stopDate)
    configParser.set(_SYMBOLS_SECTION, symbol, dateRange)
    datafile = '%s.db' % symbol

    with open(datafile, 'wb') as fd:
        fd.write(data)

    with open(SYMBOLS_STAT_FILE, 'wt') as statfd:
        configParser.write(statfd)
