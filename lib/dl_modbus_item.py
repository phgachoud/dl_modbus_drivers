#!/usr/bin/env python3
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#       DESCRIPTION: modbus register
#

#		*************************************************************************************************
#       @author: Philippe Gachoud
#       @creation: 20210329
#       @last modification:
#       @version: 1.0
#       @URL: $URL
#		*************************************************************************************************
#		MIT LICENSE
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# INCLUDES
try:
	import sys
	import os.path
#	import os, errno
	import logging # http://www.onlamp.com/pub/a/python/2005/06/02/logging.html
	from logging import handlers
#	import argparse
#	from datetime import datetime, date, time, timedelta
##	import jsonpickle # pip install jsonpickle
##	import json
except ImportError as l_err:
	print("ImportError: {0}".format(l_err))
	raise l_err

class DlModbusItem(object):

# CONSTANTS

# VARIABLES
	_address = None #Register start address, could be 3000 or 0x3000 for example
	_description = None #An item description
	_abbreviation = None # An abbreviation
	_item = None #Raw content of register
	_unit = None #Unit of data content
	_registers_count = 1 #Quantity of registers of 16 bits that have to be read to obtain item (value)

# FUNCTIONS DEFINITION 

	def __init__(self, an_address, a_description, an_abbreviation, a_registers_count, a_unit, a_default_item):
		"""
			Initialize
		"""
		self._address = int(an_address)
		self._description = a_description
		self._abbreviation = an_abbreviation
		self._registers_count = a_registers_count
		self._item = a_default_item
		self._unit = a_unit


	def out(self):
		"""
		returns a string with human readable output for current object
		"""
		l_res = self._description + ' (' + self._abbreviation + '): '
		l_res += '{} '.format(self._item) + self._unit
		return l_res
		
		
