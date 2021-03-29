#!/usr/bin/env python3
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#       DESCRIPTION: Logger, use new_logger function
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
	from pymodbus.payload import BinaryPayloadDecoder
	from pymodbus.constants import Endian
except ImportError as l_err:
	print("ImportError: {0}".format(l_err))
	raise l_err

class DlBytesDecoder(object):

# CONSTANTS

# VARIABLES
	_byte_order = Endian.Little
	_word_order = Endian.Little



# FUNCTIONS DEFINITION 

	#def __init__(self):
		

	def uint_16(self, a_register_read_res, a_logger=None):
		"""
		a_register_read_res: result of read_input_registers
		"""
		if a_logger: a_logger.debug("set_value_with_raw, u_int_16->before decoder:{}".format(a_register_read_res.registers))
		l_decoder = BinaryPayloadDecoder.fromRegisters(a_register_read_res.registers, byteorder=self._byte_order, wordorder=self._word_order) #https://pymodbus.readthedocs.io/en/latest/source/example/modbus_payload.html
		#https://pymodbus.readthedocs.io/en/v1.3.2/library/payload.html?highlight=binarypayloaddecoder#pymodbus.payload.BinaryPayloadDecoder
		l_res = l_decoder.decode_16bit_uint()
		#a_logger.debug("set_value_with_raw->after decoder:{} raw_int:{} raw_register_hexa:0x{}".format(l_v, a_register_read_res.registers[0], '{:02X}'.format(a_register_read_res.registers[0])))
		return l_res

	def uint_32(self, a_register_read_res, a_logger=None):
		"""
		a_register_read_res: result of read_input_registers
		"""
		if a_logger: a_logger.debug("set_value_with_raw, u_int_16->before decoder:{}".format(a_register_read_res.registers))
		l_decoder = BinaryPayloadDecoder.fromRegisters(a_register_read_res.registers, byteorder=self._byte_order, wordorder=self._word_order) #https://pymodbus.readthedocs.io/en/latest/source/example/modbus_payload.html
		#https://pymodbus.readthedocs.io/en/v1.3.2/library/payload.html?highlight=binarypayloaddecoder#pymodbus.payload.BinaryPayloadDecoder
		l_res = l_decoder.decode_32bit_uint()
		#a_logger.debug("set_value_with_raw->after decoder:{} raw_int:{} raw_register_hexa:0x{}".format(l_v, a_register_read_res.registers[0], '{:02X}'.format(a_register_read_res.registers[0])))
		return l_res

